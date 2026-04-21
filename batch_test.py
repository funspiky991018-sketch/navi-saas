import csv
import requests

API_URL = "http://127.0.0.1:8000/example/analyze"  # your running FastAPI endpoint
input_csv = "resumes.csv"
output_csv = "analysis_results.csv"
LOW_SCORE_THRESHOLD = 70  # highlight low-score resumes

REQUIRED_SKILLS = ["Python", "FastAPI", "REST API", "data processing"]

# Initialize skill gap counter
skill_gap_counter = {skill: 0 for skill in REQUIRED_SKILLS}

with open(input_csv, newline='', encoding='utf-8') as infile, \
     open(output_csv, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    fieldnames = ['name', 'match_score', 'missing_skills', 'needs_improvement']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for idx, row in enumerate(reader, start=1):
        resume_text = row.get('resume', '').strip()
        if not resume_text:
            print(f"[{idx}] Warning: No resume text, skipping...")
            continue

        resume_name = row.get('name', f"Resume_{idx}")

        payload = {
            "resume": resume_text,
            "job_description": """
            We are looking for a Python developer with experience in FastAPI,
            REST APIs, and data processing.
            """
        }

        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                score = data.get('match_score', 0)
                missing_skills = data.get('missing_skills', [])

                for skill in missing_skills:
                    skill_gap_counter[skill] += 1

                needs_improvement = "Yes" if score < LOW_SCORE_THRESHOLD else "No"

                writer.writerow({
                    'name': resume_name,
                    'match_score': score,
                    'missing_skills': ", ".join(missing_skills) if missing_skills else "None",
                    'needs_improvement': needs_improvement
                })

                print(f"[{idx}] {resume_name} - Score: {score}% - Missing: {missing_skills if missing_skills else 'None'} - Needs Improvement: {needs_improvement}")
            else:
                print(f"[{idx}] Failed: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"[{idx}] Error contacting API:", e)

print("\nSkill Gap Summary:")
for skill, count in skill_gap_counter.items():
    print(f"- {skill}: missing in {count} resume(s)")

print(f"\nAll resumes processed. Results saved to '{output_csv}'")







