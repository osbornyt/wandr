import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from form_app.utils import populate_shift_ticket_form, populate_evaluation_form
from main.models import UserForm, AnswerField


def generate_shift_ticket_form(request, user_form_id):
    try:
        # fetch user_form data answers
        form_data = AnswerField.objects.filter(userform=user_form_id)

        # inject the data to the template form
        populate_shift_ticket_form(form_data)

        # return new/filled form
        return redirect('/media/pdfs/generated.pdf')
    except Exception as e:
        print(f'An error occurred: {e}')
        raise Exception("Something went wrong!")


# establish form completion status
def are_filled_check(request, user_form_id):
    try:
        user_form = UserForm.objects.get(pk=user_form_id)
        print('location => ', user_form.form_id.json_location)
        with open('media/' + str(user_form.form_id.json_location), 'r') as json_file:
            form_template = json.load(json_file)

        expected_questions = [
            {"question_number": q["No"], "question_page": q["Page"]}
            for q in form_template["data"]
        ]

        form_answers = AnswerField.objects.filter(userform=user_form_id)
        answered_map = {
            (a.question_number, a.question_page): a.answer
            for a in form_answers
        }

        unfilled = []
        for q in expected_questions:
            key = (q["question_number"], q["question_page"])
            answer = answered_map.get(key)
            if not answer or not answer.strip():
                unfilled.append(q)

        if unfilled:
            return JsonResponse({
                "are_filled": False,
                "unfilled_answers": sorted(unfilled, key=lambda a: a['question_page'])
            })

        return JsonResponse({
            "are_filled": True
        })
    except UserForm.DoesNotExist:
        return JsonResponse({'error': "UserForm not found"}, status=404)
    except FileNotFoundError:
        return JsonResponse({'error': "Template file not found"}, status=500)
    except Exception as e:
        print(f'An error occurred: {e}')
        return JsonResponse({"error": "Something went wrong!"}, status=500)


def generate_evaluation_form(request, user_form_id):
    try:
        # pluck relevant fields for evaluation form
        # fetch from RO forms

        # inject the data to the evaluation template form
        populate_evaluation_form({})

        # return new/filled form
        return redirect('/media/generated/pdfs/filled_evaluation.pdf')
    except Exception as e:
        print(f'An error occurred: {e}')
        raise Exception("Something went wrong!")