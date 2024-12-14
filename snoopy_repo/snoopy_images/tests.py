from django.test import TestCase, Client
from django.urls import reverse
from .models import Image, User
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image as PILImage  

class ImageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.image = Image.objects.create(owner=self.user, image='images/test.jpg', description='test image')

    def test_image_str(self):
        self.assertEqual(str(self.image), 'test image')
    
    def test_image_owner(self):
        self.assertEqual(self.image.owner, self.user)
    
    def test_image_image(self):
        self.assertEqual(self.image.image, 'images/test.jpg')
    
    def test_image_description(self):
        self.assertEqual(self.image.description, 'test image')
    
    def test_image_created_at(self):
        self.assertIsNotNone(self.image.created_at)
    
    def test_image_updated_at(self):
        self.assertIsNotNone(self.image.updated_at)
    
    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')
    
    def test_user_username(self):
        self.assertEqual(self.user.username, 'testuser')
    
    def test_user_password(self):
        self.assertTrue(self.user.check_password('12345'))

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_signup(self):
        response = self.client.post(reverse('signup'), {'username': 'newuser', 'password': '12345'})
        self.assertEqual(response.status_code, 303)
        self.assertEqual(User.objects.count(), 2)  

    def test_login_view(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})
        self.assertEqual(response.status_code, 303)

    def test_logout_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 303)

    def test_index(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def temporary_image(self):
        bts = BytesIO()
        img = PILImage.new("RGB", (100, 100))
        img.save(bts, format='JPEG')
        bts.seek(0)  
        return SimpleUploadedFile("test.jpg", bts.getvalue(), content_type='image/jpeg')

    def test_upload(self):
        self.client.login(username='testuser', password='12345')
        
        test_image = self.temporary_image()
        
        response = self.client.post(reverse('upload'), {'image': test_image, 'description': 'test image'})
        
        self.assertEqual(response.status_code, 303)
        self.assertEqual(Image.objects.count(), 1, msg='Image was not created') 
        self.assertEqual(Image.objects.last().description, 'test image')