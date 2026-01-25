import os

from litellm import completion

os.environ["DEEPSEEK_API_KEY"] = "sk-62331370bfcd44ba954b6aef6a3f3c5d"


def generate_text(prompt):
    try:
        messages = [{"role": "user", "content": prompt}]

        response = completion(
            model="deepseek/deepseek-chat",
            messages=messages,
        )

        generated_text = response.choices[0].message.content
        return generated_text

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None


def main():
    prompt = "Please write a short essay about artificial intelligence."

    print("Starting content generation...")
    result = generate_text(prompt)

    if result:
        print("\nGenerated content:")
        print(result)
    else:
        print("\nGeneration failed")


def test_init() -> None:
    main()
