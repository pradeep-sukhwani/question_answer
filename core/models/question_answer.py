from django_extensions.db.models import TimeStampedModel, models


class Question(TimeStampedModel):
    title = models.CharField(max_length=225)
    question = models.TextField("Question")
    answer = models.ManyToManyField("Answer", blank=True, related_name='question_answer',
                                    help_text='Each question can have multiple answers')
    tag = models.ManyToManyField("Tag", help_text='Tag that suits the category of a question',
                                 related_name='question_tag')
    asked_by = models.ForeignKey("Profile", on_delete=models.SET_NULL, null=True, related_name='question_asked_by')
    up_vote = models.IntegerField("Up-vote", default=0)
    down_vote = models.IntegerField("Up-vote", default=0)
    reputation = models.IntegerField("Reputation", default=1)

    def __str__(self):
        return 'u{id}_{title}'.format(id=self.id, title=self.title)


class Answer(TimeStampedModel):
    answer = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='answer_parent',
                               help_text='User can reply on the answer as well')
    answer_by = models.ForeignKey("Profile", on_delete=models.SET_NULL, null=True, related_name='answer_answer_by')
    up_vote = models.IntegerField("Up-vote", default=0)
    down_vote = models.IntegerField("Up-vote", default=0)
    accepted_or_not = models.BooleanField(default=False, help_text='User can accept the answer')
    favourite = models.IntegerField(default=0, help_text='User can like the answer')

    def __str__(self):
        return 'u{id}'.format(id=self.id)
