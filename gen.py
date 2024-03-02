import openai

openai.api_key = "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"


def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print("An error occurred:", str(e))
        return "Sorry, something went wrong."


if __name__ == "__main__":
    topic = input("Enter the topic: ")

    paragraph_title_prompt = "act as a professional content writer write a short one minute paragraph in the form of paragraph title = " + topic
    gpt_response_title = chat_with_gpt(paragraph_title_prompt)

    print("Paragraph Title:", gpt_response_title)

    unsplash_keywords_prompt = "i want use stock images from the unsplash. so provide some 5 relevant keyword to find exact same images on unsplash topic =" + topic
    gpt_response_keywords = chat_with_gpt(unsplash_keywords_prompt)

    unsplash_keywords_list = gpt_response_keywords.split("\n")

    print("Relevant Keywords:")
    for keyword in unsplash_keywords_list:
        print(keyword)

    responses_list = [gpt_response_title] + unsplash_keywords_list
    print("Responses stored in a list:", responses_list)
