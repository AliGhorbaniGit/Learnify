from django.test import TestCase
from django.contrib.messages import get_messages 

from django.shortcuts import reverse
from django.contrib.auth import get_user_model

from .models import Language
from course.models import Tag, Course, Teacher
from common.models import Category
from ticket.models import Ticket

User = get_user_model()

class CoreVIewsTests(TestCase):
    
    @classmethod 
    def setUpTestData(cls):
        # Create a test tag  
        cls.tag = Tag.objects.create(title='test_tag', slug='test-tag')
        # Create a test language  
        cls.language = Language.objects.create(name='test_language')
        # Create some categories  
        cls.category = Category.objects.create(title='Test_Category',slug='test-cat')  
        # Create a test user  
        cls.user = User.objects.create_user(  
            username='testuser',  
            email='testuser@example.com',  
            password='testpassword'  )
        # Create a test teacher  
        cls.teacher = Teacher.objects.create(user=cls.user)
        # Create a test course  
        cls.course = Course.objects.create(
            title = 'coure_test',
            slug = 'course-test',
            teacher = cls.teacher,
            status = 'a',
        )



    def test_home_view(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('core/index.html')
        self.assertContains(response, self.tag)
        self.assertContains(response, self.course)
        self.assertTrue('random_tags' in response.context) 
        self.assertTrue('top_rated_courses' in response.context)   

    def test_filter_view(self):
        # when the slug not found
        response = self.client.get(reverse('core:filter', kwargs={'slug':self.course.slug}))
        self.assertEqual(response.status_code, 404)
        # when the slug found
        response = self.client.get(reverse('core:filter', kwargs={'slug':self.category.slug}))
        # when tag not mached
        self.assertEqual(response.status_code, 302)
        # when tag mached
        self.course.category.set([self.category])
        response = self.client.get(reverse('core:filter', kwargs={'slug':self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'core/search-and-filter-list.html' )
        
        # Check context contains articles and courses  
        self.assertIn('blogs', response.context)  
        self.assertIn('courses', response.context)  
        self.assertIn('categories', response.context)  
        self.assertIn('top_rated_courses', response.context)  

        # Ensure the courses are in context  
        self.assertIn(self.course, response.context['courses'])  


    def test_about_view(self):
        response = self.client.get(reverse('core:about-us'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('top_rated_courses', response.context)
        self.assertIn('about_page', response.context)
        self.assertTemplateUsed(response, 'core/about.html')


    def test_faq_view(self):
        response = self.client.get(reverse('core:faq'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('top_rated_courses', response.context)
        self.assertTemplateUsed(response, 'core/faq.html')


    def test_search_view(self):
        # check get request must redirect
        response = self.client.get(reverse('core:search'))
        self.assertEqual(response.status_code, 302)
        # check valid form request
        response = self.client.get(reverse('core:search'),{
            'query':'test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('courses', response.context)  
        self.assertIn('blogs', response.context)  
        self.assertIn('categories', response.context)  
        self.assertIn('top_rated_courses', response.context)  
        self.assertTemplateUsed(response, 'core/search-and-filter-list.html')
        # check id not query.strip request
        response = self.client.get(reverse('core:search'),{
            'query':''
        })
        self.assertEqual(response.status_code, 302)


    def test_profile_view(self):
        # check logedout user, must be redirect
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.status_code, 302)
        # check login user
        login_response = self.client.post(reverse('account_login'), {  
            'login': 'testuser',  
            'password': 'testpassword'  
        })   
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('language_form', response.context)  
        self.assertIn('custom_user', response.context) 
        self.assertTemplateUsed(response, 'core/profile.html')
        # chech post request to change the language
        response = self.client.post(reverse('core:profile'),{
            'name':self.language
        })
 
        messages = list(get_messages(response.wsgi_request))  
        self.assertTrue(any('Language updated' in str(m) for m in messages))  

    def test_profile_overview(self):
        # check not existed user, must be redirect
        response = self.client.get(reverse('core:profile-overview', args=['not-exist']))
        self.assertEqual(response.status_code, 404)
        # check existed user
        response = self.client.get(reverse('core:profile-overview', args=[self.user]))
        self.assertEqual(response.status_code, 200)

        self.assertIn('user', response.context)  
        self.assertIn('articles', response.context) 
        self.assertIn('courses', response.context) 
        self.assertTemplateUsed(response, 'core/profile-overview.html')


    def test_contactus_view(self):
        response = self.client.get(reverse('core:contact-us'))
        self.assertEqual(response.status_code, 200)
        # send a contact form with logout user
        response = self.client.post(reverse('core:contact-us'),{
            'title':'test',
            'description':'test'

        })
        self.assertEqual(response.status_code, 302)
        # send a contact form with authenticated user and valid format
        self.client.post(reverse('account_login'), {  
            'login': 'testuser',  
            'password': 'testpassword'  
        })   
        response = self.client.post(reverse('core:contact-us'),{
            'title':'This is a detailed title of the issue.',
            'description':'This is a detailed description of the issue.This is a detailed description of the issue.',

        })
        self.assertRedirects(response, self.client.session.get('_redirect_to') or '/')  
        messages = list(get_messages(response.wsgi_request))  
        self.assertTrue(any('Your ticket has been submitted' in str(m) for m in messages))  
        

        # send a contact form with authenticated user and invalid format
        response = self.client.post(reverse('core:contact-us'),{
            'title':'This is invalid',
            'description':'This is invalid',

        })
        self.assertTrue(any('not sent' in str(m) for m in messages))  
        self.assertEqual(response.status_code, 302)



    def test_profile_update(self):
        # when user is not authenticated
        response = self.client.get(reverse('core:profile-update'))
        self.assertEqual(response.status_code, 302)
        # when user is authenticated
        self.client.post(reverse('account_login'), {  
            'login': 'testuser',  
            'password': 'testpassword'  
        })   
        response = self.client.get(reverse('core:profile-update'))
        self.assertEqual(response.status_code, 200)
        # send a post request with invalid data
        response = self.client.post(reverse('core:profile-update'), {
            'false':'invalid'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/profile-update.html')
        self.assertIn('user_form', response.context)
        self.assertIn('profile_form', response.context)
        self.assertIn('profile', response.context)
  

    def test_TermsList(self):
        response = self.client.get(reverse('core:terms'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/terms-list.html')
        self.assertIn('top_rated_courses', response.context)



class AllauthLoginViewsTestCase(TestCase):  

    @classmethod  
    def setUpTestData(cls): 
        # Create a test user  
        cls.user = User.objects.create_user(  
            username='testuser',  
            email='testuser@example.com',  
            password='testpassword'  )

    def test_login_view_get(self):  
        """Test GET request to the login view"""  
        response = self.client.get(reverse('account_login'))  
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'account/login.html')  # Ensure the correct template is used  

    def test_login_view_post_valid(self):  
        """Test valid POST request to the login view"""  
        response = self.client.post(reverse('account_login'), {  
            'login': 'testuser',  
            'password': 'testpassword'  
        })  
        self.assertEqual(response.status_code, 302)  # Should redirect after successful login  
        self.assertTrue(response.wsgi_request.user.is_authenticated)  # Ensure the user is now authenticated  
        self.assertRedirects(response, '/')  # Check that it redirects to the home page (or desired URL) 
         
    def test_allauth_login(self):
        """Test GET request to the login view"""  
        self.response = self.client.get(reverse('account_login')) 
        self.assertTrue(self.response)
        self.assertEqual(self.response.status_code, 200)

        self.client.post(self.response, {'username':'testuser', 'password':'testpassword'})
            
        response = self.client.get(reverse('account_login'))  
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'account/login.html') 