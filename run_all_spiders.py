import subprocess
import time
from datetime import datetime
import glob
import os
import json
import openai

def run_spider(name):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] ▶ Starting {name}")
    result = subprocess.run(
        ['scrapy', 'crawl', name],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"[{datetime.now():%H:%M:%S}] ✓ {name} finished")
    else:
        print(f"[{datetime.now():%H:%M:%S}] ✗ {name} failed:")
        print(result.stderr)
    return result.returncode == 0

def get_latest_json_file(output_dir="output"):
    files = glob.glob(os.path.join(output_dir, "financial_news_*.json"))
    if not files:
        return None
    return max(files, key=os.path.getctime)

def process_with_openai(articles, prompt_template, output_json="output/openai_cnbc_responses.json"):
    responses = []
    client = openai.OpenAI(
        api_key="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"
    )
    for article in articles:
        prompt = prompt_template.format(
            title=article.get('title', ''),
            content=article.get('content', '')
        )
        print(f"\n---\nPrompting OpenAI for article: {article.get('title', '')[:60]}...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )
        summary = response.choices[0].message.content
        print(f"OpenAI response:\n{summary}\n")
        responses.append({
            "title": article.get('title', ''),
            "url": article.get('url', ''),
            "openai_response": summary
        })
    # Save all responses to a JSON file
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
    print(f"\nAll OpenAI responses saved to {output_json}")
    return responses

def final_summary_with_openai(summaries, api_key, output_txt="output/openai_final_summary.txt"):
    client = openai.OpenAI(api_key=api_key)
    combined_text = "\n\n".join(summaries)
    final_prompt = (
        "You are 'The Financial Current', a witty, sharp, and slightly irreverent financial news columnist. "
        "Your readers are busy professionals and curious individuals who want to stay informed about finance "
        "without getting bogged down in jargon or dry details. They appreciate clarity, conciseness, and a good laugh. "
        "Your goal is to make finance genuinely enjoyable and easy to digest.\n\n"
        "Below is a collection of summarized financial news articles from today. Your task is to craft a compelling, "
        "single-section daily news blast that reads like a premium financial column. Focus on the most impactful "
        "or interesting developments, distilling complex topics into their essential, actionable points. "
        "Do NOT simply list summaries. Instead, weave them into a cohesive narrative, highlighting key themes and implications.\n\n"
        "Here's what your daily digest MUST include:\n"
        "-   **An engaging and slightly humorous headline** that grabs attention.\n"
        "-   **An opening paragraph** that sets the tone and introduces the day's major financial vibe.\n"
        "-   **A concise, flowing summary of the day's top financial news.** Combine related topics where possible. "
        "    Focus on the *what happened*, the *why it matters*, and *what the immediate implications are*.\n"
        "-   **Sprinkle in a touch of humor or a witty observation** where appropriate, but never at the expense of clarity or professionalism.\n"
        "-   **Prioritize the most significant news.** You do not need to cover every single article. If a piece of news is minor or redundant, leave it out.\n"
        "-   **Avoid bulleted lists for the main content.** Write in full paragraphs, like a narrative article.\n"
        "-   **Do NOT include individual article links or titles next to each summary within the main body.** "
        "    If you deem a source particularly crucial, you can reference it naturally within the text (e.g., 'According to Reuters...').\n"
        "-   **Conclude with a brief, insightful, and slightly humorous closing thought or a forward-looking statement.**\n"
        "-   **Maintain a maximum length of 400 words** to keep it punchy and digestible. Focus on quality over quantity.\n\n"
        "Here are today's article summaries for your analysis and integration:\n"
        f"{combined_text}"
    )
    print("\n---\nPrompting OpenAI for a final summary of all articles...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": final_prompt}],
        max_tokens=300,
        temperature=0.7,
    )
    final_summary = response.choices[0].message.content
    print(f"\nFinal OpenAI summary of all articles:\n{final_summary}\n")
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(final_summary)
    print(f"Final summary saved to {output_txt}")

if __name__ == '__main__':
    # Run all spiders
    SPIDERS = [
        'cnbc',
        'yahoo_finance',
        'marketwatch',
        'bloomberg',
        'financial_times',
        'wsj',
        'forbes',
        'businessinsider',
        'bbc_business',
        'reuters',
        'morningstar',
        'economist',
        'nasdaq',
        'cnn_business',
    ]
    DELAY = 1  # seconds between spiders

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Starting all spiders")
    for spider in SPIDERS:
        run_spider(spider)
        time.sleep(DELAY)
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] All spiders done.")

    # Find the latest output file
    latest_json = get_latest_json_file()
    if latest_json:
        print(f"Processing articles from {latest_json}")
        with open(latest_json, "r", encoding="utf-8") as f:
            articles = json.load(f)

        # Prompt OpenAI for each article
        prompt_template = (
            "Summarize this news article in 2 sentences.\n"
            "Title: {title}\n"
            "Content: {content}\n"
        )

        responses = process_with_openai(articles, prompt_template)

        # Feed all summaries into OpenAI for a final summary
        all_summaries = [resp["openai_response"] for resp in responses]
        final_summary_with_openai(
            all_summaries,
            api_key="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"
        )
    else:
        print("No output JSON file found.")