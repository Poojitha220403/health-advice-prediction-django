from .models import Post
# Retrieve all Post objects
posts = Post.objects.all()

# Print attributes of each Post object
for post in posts:
    print(post.attribute_1, post.attribute_2)
