from django.test import TestCase  
from django.urls import reverse  
from django.contrib.auth import get_user_model  
from .models import Article, ArticleComment, ArticleRate, Writer  
from .forms import ArticleCommentForm, ArticleRatingForm  
from common.models import Category

User = get_user_model()  

class BlogViewsTestCase(TestCase):  

    @classmethod  
    def setUpTestData(cls): 
        # Create a test user  
        cls.user = User.objects.create_user(  
            username='testuser',  
            email='testuser@example.com',  
            password='testpassword'  )
        # Create a test writer  
        cls.writer = Writer.objects.create(user=cls.user)  
        # Create some categories  
        cls.category = Category.objects.create(title='Test_Category',slug='test-cat')  
        # Create a test article  
        cls.article = Article.objects.create(  
            title='Test_Article',  
            slug='test-article',  
            writer=cls.writer, 
            intro_txt='test intro ...',
            description='test description....',
            status='a',
        )  
        # Associate the article with a category  
        cls.article.category.add(cls.category)  


    def test_blog_list_view(self):  
        response = self.client.get(reverse('blog:blogs-list'))  
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'blog/blog-list.html')  
        self.assertContains(response, self.article.title)  
        # send a invalid request method
        response = self.client.post(reverse('blog:blogs-list'))
        self.assertEqual(response.status_code, 405)    

    def test_blog_detail_view(self):  
        response = self.client.get(reverse('blog:blog-detail', kwargs={'slug': self.article.slug}))  
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'blog/blog-detail.html')  
        self.assertContains(response, self.article.title)  

    def test_add_article_view(self):  
        # User must be logged in to access this view  
        response = self.client.get(reverse('blog:add-article'))  
        self.assertEqual(response.status_code, 302)  # Redirected to login  

        # Log in the user  
        login_response = self.client.post(reverse('account_login'), {  
            'login': 'testuser',  
            'password': 'testpassword'  
        })  
        self.assertTrue(login_response.wsgi_request.user.is_authenticated)

        response = self.client.get(reverse('blog:add-article'))  
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'blog/add-article.html')  
        
        # Test posting a article  
        response = self.client.post(reverse('blog:add-article'), {  
            'title':'Test2_Article',  
            'slug':'test2-article',  
            'intro_txt':'intro_txt must be at least 100 characters long.intro_txt must be at least 100 characters long.intro_txt must be at least 100 characters long.intro_txt must be at least 100 characters long.',
            'description':'description must be at least 100 characters long.description must be at least 100 characters long.description must be at least 100 characters long.description must be at least 100 characters long.',
            'image':'somethings.jpg',
        })  
        self.assertEqual(response.status_code, 302)  # Should redirect after successful submission  
        self.assertTrue(Article.objects.filter(title='Test2_Article').exists())  

    def test_comment_submission(self):  
        #Log in the user  
        login_response = self.client.post(reverse('account_login'), {  
            'login': 'testuser',  
            'password': 'testpassword'  
        })   
        self.assertTrue(login_response.wsgi_request.user.is_authenticated)

        response = self.client.post(reverse('blog:blog-detail', kwargs={'slug': self.article.slug}),  
             {  
                'text': 'Comment must be at least 5 characters long.'  ,
                'comment_form': {  
                'text': 'This is a test comment.'  
            }  
            }  
        )  
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(ArticleComment.objects.all().count() == 1)
        self.assertTrue(ArticleComment.objects.filter(article=self.article).exists())  

    def test_rating_submission(self):  
        #Log in the user  
        login_response = self.client.post(reverse('account_login'), {  
            'login': 'testuser',  
            'password': 'testpassword'  
        })   
        response = self.client.post(reverse('blog:blog-detail', kwargs={'slug': self.article.slug}), { 
            'score':1, 
            'rating_form': {  
                'score': 5  # score ranges from 1 to 5  
            }  
        })  
        self.assertEqual(response.status_code, 302)  # Redirect after rating  
        self.assertTrue(ArticleRate.objects.filter(article=self.article, user=self.user).exists())  

    def test_access_without_login(self):  
        response = self.client.get(reverse('blog:add-article'))  
        self.assertEqual(response.status_code, 302)  # User must be logged in  

