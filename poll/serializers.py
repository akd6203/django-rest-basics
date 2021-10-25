from rest_framework import serializers
from poll.models import Question, Choice, Tag

class ChoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Choice
        fields=[
            'id',
            'question',
            'text'
        ]
        # depth=1
        read_only_fields = ('question',)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields=('name',)
        
class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    tags = TagSerializer(many=True)
    class Meta:
        model = Question
        fields=('id',
            'title','status','created_by','choices','tags')

    def create(self, validated_data):
        choices=validated_data.pop('choices')
        question = Question.objects.create(**validated_data)
        for choice in choices:
            Choice.objects.create(**choice, question=question)
        return question

    def update(self, instance, validated_data):
        choices=validated_data.pop('choices')
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        keep_ids = []
        existing_ids = [c.id for c in instance.choices]

        for choice in choices:
            if "id" in choice.keys():
                if Choice.objects.filter(id=choice['id']).exists():
                    ch = Choice.objects.get(id=choice['id'])
                    ch.text=choice.get('text',ch.text)
                    ch.save()
                    keep_ids.append(ch.id)
                else:
                    continue
            else:
                ch = Choice.objects.create(**choice, question=instance)
                keep_ids.append(ch.id)
        
        for choice in instance.choices:
            if choice.id not in keep_ids:
                choice.delete()
        
        return instance

        