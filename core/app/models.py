from django.db import models

# Create your models here.
class Chat(models.Model):
    created = models.DateTimeField(auto_now_add = True, null = True)

    @property
    def title(self):
        if self.message_set.exists():
            return self.message_set.order_by("created").first().content
        return "Nowy chat"
    
    @property
    def is_empty(self):
        return not self.message_set.exists()
    
    def __str__(self) -> str:
        return str(self.id)

class Message(models.Model):
    content = models.CharField(max_length=500)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, blank=True, null=True)
    ai_response = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return "chat: " + str(self.chat) + " | content: " + str(self.content)