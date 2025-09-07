## Spheres (spheres master list)

| Short Name | Full Name                  | Emoji |
|:-----------|:--------------------------|:------|
| love       | Love & Relationships      | 💖    |
| family     | Family                    | 🏡    |
| friends    | Friends                   | 🤝    |
| career     | Career                    | 💼    |
| physical   | Physical Health           | ♂️    |
| mental     | Mental Health             | 🧠    |
| hobby      | Hobbies & Interests       | 🎨    |
| wealth     | Wealth                    | 💰    |

<!-- Add new spheres and aliases as needed -->

---
alias: "HPI Questions Base (EN)"
tags:
  - hpi/questions
  - hpi/database
hpi_weights: {
  "💖":0.125, 
  "🏡":0.125, 
  "🤝":0.125, 
  "💼":0.125, 
  "♂️":0.125, 
  "🧠":0.125, 
  "🎨":0.125, 
  "💰":0.125
}
version: "2.5.0-en"
---

# 📝 HPI Questions Base (EN)

## 💖 Love & Relationships
```json
[
  {
    "type": "basic",
    "text": "How often do you spend quality time together?",
    "options": ["Rarely or never", "Sometimes", "Often", "Regularly and mindfully"]
  },
  {
    "id": "1.1",
    "type": "basic",
    "text": "Frequency of quality time",
    "options": ["Less than once a week", "1-2 times a week", "3-4 times a week", "Daily"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "1.2",
    "type": "basic",
    "text": "Alignment of life goals",
    "options": ["Completely different plans", "Some overlap", "Mostly aligned", "Fully synchronized"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "1.3",
    "type": "basic",
    "text": "Conflict resolution",
    "options": ["Frequent quarrels without resolution", "Occasional disputes but compromises", "Rare conflicts, constructive", "Almost never conflict"],
    "scores": [4, 3, 2, 1],
    "inverse": true
  },
  {
    "id": "1.4",
    "type": "basic",
    "text": "Support in crises",
    "options": ["Partner does not participate", "Minimal help", "Actively supports", "Full joint effort"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "1.5",
    "type": "basic",
    "text": "Showing attention and care",
    "options": ["Rarely or never", "Sometimes", "Often", "Constantly and in various ways"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "1.6",
    "type": "basic",
    "text": "Feeling of love and acceptance",
    "options": ["Not at all / Very little", "To some extent", "To a significant extent", "Absolutely / Completely"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "p1",
    "type": "pro",
    "category": "problems",
    "text": "My problems",
    "description": "What worries me in my relationship...",
    "fields": {
      "text": "string",
      "severity": "number",
      "created_at": "datetime",
      "status": "active|resolved"
    }
  },
  {
    "id": "g1",
    "type": "pro",
    "category": "goals",
    "text": "My goals",
    "description": "What I want to achieve in my relationship...",
    "fields": {
      "text": "string",
      "deadline": "date",
      "priority": "number",
      "status": "planned|in_progress|achieved"
    }
  },
  {
    "id": "b1",
    "type": "pro",
    "category": "blockers",
    "text": "My blockers",
    "description": "What prevents improvement in my relationship...",
    "fields": {
      "text": "string",
      "impact_level": "number",
      "related_goals": ["goal_ids"]
    }
  },
  {
    "id": "m1",
    "type": "pro",
    "category": "metrics",
    "text": "My metrics",
    "description": "What can I measure in my relationship...",
    "metrics": [
      {"name": "Hours together per week", "unit": "h", "type": "number"},
      {"name": "Number of joint activities per month", "unit": "pcs", "type": "number"},
      {"name": "Quality of communication", "unit": "1-10", "type": "scale"}
    ]
  },
  {
    "id": "a1",
    "type": "pro",
    "category": "achievements",
    "text": "My achievements",
    "description": "What I already have today in my relationship...",
    "fields": {
      "text": "string",
      "date_achieved": "datetime",
      "impact_areas": ["sphere_ids"]
    }
  }
]
```
## 🏡 Family
```json
[
  {
    "type": "basic",
    "text": "How often do you spend time with your family?",
    "options": ["Rarely", "Sometimes", "Often", "Very often"]
  },
  {
    "id": "2.1",
    "type": "basic",
    "text": "Frequency of family visits",
    "options": ["Less than once a month", "1-2 times a month", "1-2 times a week", "3+ times a week"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "2.2",
    "type": "basic",
    "text": "Quality of family communication",
    "options": ["Superficial topics", "Personal questions rarely", "Regularly share experiences", "Complete mutual trust"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "2.3",
    "type": "basic",
    "text": "Joint family activities",
    "options": ["No common activities", "Passive leisure (cafe/cinema)", "Active hobbies (sports/travel)", "Joint projects/business"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "2.4",
    "type": "basic",
    "text": "Conflicts with family members",
    "options": ["Frequent misunderstandings", "Periodic disagreements", "Rare situations", "Complete mutual understanding"],
    "scores": [4, 3, 2, 1],
    "inverse": true
  },
  {
    "id": "2.5",
    "type": "basic",
    "text": "Support from family in crises",
    "options": ["Family does not help", "Help only with words", "Active participation", "Full all-round support"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "2.6",
    "type": "basic",
    "text": "Feeling of family well-being",
    "options": ["Very poor", "Poor", "Good", "Very good"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "p2",
    "type": "pro",
    "category": "problems",
    "text": "My problems",
    "description": "What worries me in my family...",
    "fields": {
      "text": "string",
      "severity": "number",
      "created_at": "datetime",
      "status": "active|resolved"
    }
  },
  {
    "id": "g2",
    "type": "pro",
    "category": "goals",
    "text": "My goals",
    "description": "What I want to achieve in my family...",
    "fields": {
      "text": "string",
      "deadline": "date",
      "priority": "number",
      "status": "planned|in_progress|achieved"
    }
  },
  {
    "id": "b2",
    "type": "pro",
    "category": "blockers",
    "text": "My blockers",
    "description": "What prevents improvement in my family...",
    "fields": {
      "text": "string",
      "impact_level": "number",
      "related_goals": ["goal_ids"]
    }
  },
  {
    "id": "m2",
    "type": "pro",
    "category": "metrics",
    "text": "My metrics",
    "description": "What can I measure in my family...",
    "metrics": [
      {"name": "Number of family visits per month", "unit": "pcs", "type": "number"},
      {"name": "Time spent communicating per week", "unit": "h", "type": "number"},
      {"name": "Quality of family communication", "unit": "1-10", "type": "scale"}
    ]
  },
  {
    "id": "a2",
    "type": "pro",
    "category": "achievements",
    "text": "My achievements",
    "description": "What I already have today in my family...",
    "fields": {
      "text": "string",
      "date_achieved": "datetime",
      "impact_areas": ["sphere_ids"]
    }
  }
]
```
## 🤝 Friends
```json
[
  {
    "type": "basic",
    "text": "How often do you meet with friends?",
    "options": ["Rarely", "Sometimes", "Often", "Very often"]
  },
  {
    "id": "3.1",
    "type": "basic",
    "text": "Frequency of meetings",
    "options": ["Less than once a month", "1-2 times a month", "1-2 times a week", "3+ times a week"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "3.2",
    "type": "basic",
    "text": "Depth of communication",
    "options": ["Superficial topics", "Personal questions rarely", "Regularly share experiences", "Complete mutual trust"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "3.3",
    "type": "basic",
    "text": "Joint activities",
    "options": ["No common activities", "Passive leisure (cafe/cinema)", "Active hobbies (sports/travel)", "Joint projects/business"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "3.4",
    "type": "basic",
    "text": "Conflicts with friends",
    "options": ["Frequent misunderstandings", "Periodic disagreements", "Rare situations", "Complete mutual understanding"],
    "scores": [4, 3, 2, 1],
    "inverse": true
  },
  {
    "id": "3.5",
    "type": "basic",
    "text": "Support from friends in crises",
    "options": ["Friends do not help", "Help only with words", "Active participation", "Full all-round support"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "3.6",
    "type": "basic",
    "text": "Having a close friend",
    "options": ["No such friend", "Probably not", "Rather yes, there is", "Definitely yes, there is"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "p3",
    "type": "pro",
    "category": "problems",
    "text": "My problems",
    "description": "What worries me in my friendships...",
    "fields": {
      "text": "string",
      "severity": "number",
      "created_at": "datetime",
      "status": "active|resolved"
    }
  },
  {
    "id": "g3",
    "type": "pro",
    "category": "goals",
    "text": "My goals",
    "description": "What I want to achieve in my friendships...",
    "fields": {
      "text": "string",
      "deadline": "date",
      "priority": "number",
      "status": "planned|in_progress|achieved"
    }
  },
  {
    "id": "b3",
    "type": "pro",
    "category": "blockers",
    "text": "My blockers",
    "description": "What prevents improvement in my friendships...",
    "fields": {
      "text": "string",
      "impact_level": "number",
      "related_goals": ["goal_ids"]
    }
  },
  {
    "id": "m3",
    "type": "pro",
    "category": "metrics",
    "text": "My metrics",
    "description": "What can I measure in my friendships...",
    "metrics": [
      {"name": "Number of meetings per month", "unit": "pcs", "type": "number"},
      {"name": "Time spent communicating per week", "unit": "h", "type": "number"},
      {"name": "Quality of friendship", "unit": "1-10", "type": "scale"}
    ]
  },
  {
    "id": "a3",
    "type": "pro",
    "category": "achievements",
    "text": "My achievements",
    "description": "What I already have today in my friendships...",
    "fields": {
      "text": "string",
      "date_achieved": "datetime",
      "impact_areas": ["sphere_ids"]
    }
  }
]
```
## 💼 Career
```json
[
  {
    "type": "basic",
    "text": "How satisfied are you with your professional growth?",
    "options": ["Not satisfied", "Partially satisfied", "Satisfied", "Very satisfied"]
  },
  {
    "id": "4.1",
    "type": "basic",
    "text": "Alignment of activity with your values",
    "options": ["Complete contradiction", "Partial match", "Mostly matches", "Full harmony"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "4.2",
    "type": "basic",
    "text": "Satisfaction with income from main activity",
    "options": ["Catastrophically low", "Enough for basic needs", "Comfortable level", "Exceeds expectations"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "4.3",
    "type": "basic",
    "text": "Work-life balance",
    "options": ["Constant overwork, imbalance", "Sometimes stay late, balance is disturbed", "Clear boundaries, balance is maintained", "Full harmony and flexibility"],
    "scores": [4, 3, 2, 1],
    "inverse": true
  },
  {
    "id": "4.4",
    "type": "basic",
    "text": "Growth and development prospects in your activity",
    "options": ["Career dead end / no prospects", "Unclear prospects", "There is a plan for 1-2 years", "Clear strategy for 5+ years"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "4.5",
    "type": "basic",
    "text": "Professional development and training",
    "options": ["No training / development", "Rare courses / self-education", "Regular trainings / education", "Systematic education / constant development"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "4.6",
    "type": "basic",
    "text": "Feeling of recognition and value",
    "options": ["Not valued at all / Not enough", "Partially valued", "Mostly valued", "Highly valued and recognized"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "p4",
    "type": "pro",
    "category": "problems",
    "text": "My problems",
    "description": "What worries me in my career...",
    "fields": {
      "text": "string",
      "severity": "number",
      "created_at": "datetime",
      "status": "active|resolved"
    }
  },
  {
    "id": "g4",
    "type": "pro",
    "category": "goals",
    "text": "My goals",
    "description": "What I want to achieve in my career...",
    "fields": {
      "text": "string",
      "deadline": "date",
      "priority": "number",
      "status": "planned|in_progress|achieved"
    }
  },
  {
    "id": "b4",
    "type": "pro",
    "category": "blockers",
    "text": "My blockers",
    "description": "What prevents improvement in my career...",
    "fields": {
      "text": "string",
      "impact_level": "number",
      "related_goals": ["goal_ids"]
    }
  },
  {
    "id": "m4",
    "type": "pro",
    "category": "metrics",
    "text": "My metrics",
    "description": "What can I measure in my career...",
    "metrics": [
      {"name": "Monthly income", "unit": "$", "type": "number"},
      {"name": "New skills per quarter", "unit": "pcs", "type": "number"},
      {"name": "Job satisfaction", "unit": "1-10", "type": "scale"}
    ]
  },
  {
    "id": "a4",
    "type": "pro",
    "category": "achievements",
    "text": "My achievements",
    "description": "What I already have today in my career...",
    "fields": {
      "text": "string",
      "date_achieved": "datetime",
      "impact_areas": ["sphere_ids"]
    }
  }
]
```
## ♂️ Physical Health
```json
[
  {
    "type": "basic",
    "text": "How often do you exercise?",
    "options": ["Rarely or never", "1-2 times a week", "3-4 times a week", "5+ times a week"]
  },
  {
    "id": "5.1",
    "type": "basic",
    "text": "Physical activity",
    "options": ["Sedentary lifestyle", "1-2 workouts per week", "3-4 workouts", "5+ workouts or active work"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "5.2",
    "type": "basic",
    "text": "Sleep quality",
    "options": ["Insomnia (<4 hours) / Very poor", "Interrupted sleep (4-6 hours) / Poor", "Stable 6-7 hours / Satisfactory", "8+ hours of deep sleep / Excellent"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "5.3",
    "type": "basic",
    "text": "Quality of your nutrition",
    "options": ["Mostly unhealthy food / fast food", "Often irregular, not always healthy", "Generally regular and balanced", "Completely healthy, balanced and regular"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "5.4",
    "type": "basic",
    "text": "Regularity of medical check-ups",
    "options": ["More than 3 years ago / Do not undergo", "1-3 years ago", "Within the last year", "Every 3-6 months / Regularly as planned"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "5.5",
    "type": "basic",
    "text": "Overall energy level",
    "options": ["Constant fatigue", "Energy lasts until lunch", "Stable throughout the day", "High, even in the evening"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "5.6",
    "type": "basic",
    "text": "Bad habits",
    "options": ["Significantly worsen health", "Moderately negatively affect", "Almost do not affect / Minimal impact", "Absent / Lead a completely healthy lifestyle"],
    "scores": [4, 3, 2, 1],
    "inverse": true
  },
  {
    "id": "p5",
    "type": "pro",
    "category": "problems",
    "text": "My problems",
    "description": "What worries me in my physical health...",
    "fields": {
      "text": "string",
      "severity": "number",
      "created_at": "datetime",
      "status": "active|resolved"
    }
  },
  {
    "id": "g5",
    "type": "pro",
    "category": "goals",
    "text": "My goals",
    "description": "What I want to achieve in my physical health...",
    "fields": {
      "text": "string",
      "deadline": "date",
      "priority": "number",
      "status": "planned|in_progress|achieved"
    }
  },
  {
    "id": "b5",
    "type": "pro",
    "category": "blockers",
    "text": "My blockers",
    "description": "What prevents improvement in my physical health...",
    "fields": {
      "text": "string",
      "impact_level": "number",
      "related_goals": ["goal_ids"]
    }
  },
  {
    "id": "m5",
    "type": "pro",
    "category": "metrics",
    "text": "My metrics",
    "description": "What can I measure in my physical health...",
    "metrics": [
      {"name": "Weight", "unit": "kg", "type": "number"},
      {"name": "Workouts per week", "unit": "pcs", "type": "number"},
      {"name": "Sleep quality", "unit": "1-10", "type": "scale"}
    ]
  },
  {
    "id": "a5",
    "type": "pro",
    "category": "achievements",
    "text": "My achievements",
    "description": "What I already have today in my physical health...",
    "fields": {
      "text": "string",
      "date_achieved": "datetime",
      "impact_areas": ["sphere_ids"]
    }
  }
]
```
## 🧠 Mental Health
```json
[
  {
    "type": "basic",
    "text": "How often do you feel stressed?",
    "options": ["Never", "Rarely", "Sometimes", "Often"]
  },
  {
    "id": "6.1",
    "type": "basic",
    "text": "Stress level",
    "options": ["Very high", "High", "Moderate", "Low"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "6.2",
    "type": "basic",
    "text": "Mood stability",
    "options": ["Very unstable", "Unstable", "Stable", "Very stable"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "6.3",
    "type": "basic",
    "text": "Self-esteem",
    "options": ["Very low", "Low", "Moderate", "High"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "6.4",
    "type": "basic",
    "text": "Support from family in mental crises",
    "options": ["Family does not help", "Help only with words", "Active participation", "Full all-round support"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "6.5",
    "type": "basic",
    "text": "Feeling of mental well-being",
    "options": ["Very poor", "Poor", "Good", "Very good"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "6.6",
    "type": "basic",
    "text": "Feeling of mental health well-being",
    "options": ["Very poor", "Poor", "Good", "Very good"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "p6",
    "type": "pro",
    "category": "problems",
    "text": "My problems",
    "description": "What worries me in my mental health...",
    "fields": {
      "text": "string",
      "severity": "number",
      "created_at": "datetime",
      "status": "active|resolved"
    }
  },
  {
    "id": "g6",
    "type": "pro",
    "category": "goals",
    "text": "My goals",
    "description": "What I want to achieve in my mental health...",
    "fields": {
      "text": "string",
      "deadline": "date",
      "priority": "number",
      "status": "planned|in_progress|achieved"
    }
  },
  {
    "id": "b6",
    "type": "pro",
    "category": "blockers",
    "text": "My blockers",
    "description": "What prevents improvement in my mental health...",
    "fields": {
      "text": "string",
      "impact_level": "number",
      "related_goals": ["goal_ids"]
    }
  },
  {
    "id": "m6",
    "type": "pro",
    "category": "metrics",
    "text": "My metrics",
    "description": "What can I measure in my mental health...",
    "metrics": [
      {"name": "Hours of sleep per night", "unit": "h", "type": "number"},
      {"name": "Number of workouts per week", "unit": "pcs", "type": "number"},
      {"name": "Quality of sleep", "unit": "1-10", "type": "scale"}
    ]
  },
  {
    "id": "a6",
    "type": "pro",
    "category": "achievements",
    "text": "My achievements",
    "description": "What I already have today in my mental health...",
    "fields": {
      "text": "string",
      "date_achieved": "datetime",
      "impact_areas": ["sphere_ids"]
    }
  }
]
```
## 🎨 Hobbies & Interests
```json
[
  {
    "type": "basic",
    "text": "How often do you engage in hobbies?",
    "options": ["Never", "Rarely", "Sometimes", "Often"]
  },
  {
    "id": "7.1",
    "type": "basic",
    "text": "Hobby frequency",
    "options": ["Less than once a month", "1-2 times a month", "1-2 times a week", "3+ times a week"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "7.2",
    "type": "basic",
    "text": "Hobby satisfaction",
    "options": ["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "7.3",
    "type": "basic",
    "text": "Hobby impact on life",
    "options": ["No impact", "Little impact", "Moderate impact", "Significant impact"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "7.4",
    "type": "basic",
    "text": "Support from family in hobby crises",
    "options": ["Family does not help", "Help only with words", "Active participation", "Full all-round support"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "7.5",
    "type": "basic",
    "text": "Feeling of hobby well-being",
    "options": ["Very poor", "Poor", "Good", "Very good"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "7.6",
    "type": "basic",
    "text": "Feeling of hobbies well-being",
    "options": ["Very poor", "Poor", "Good", "Very good"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "p7",
    "type": "pro",
    "category": "problems",
    "text": "My problems",
    "description": "What worries me in my hobbies...",
    "fields": {
      "text": "string",
      "severity": "number",
      "created_at": "datetime",
      "status": "active|resolved"
    }
  },
  {
    "id": "g7",
    "type": "pro",
    "category": "goals",
    "text": "My goals",
    "description": "What I want to achieve in my hobbies...",
    "fields": {
      "text": "string",
      "deadline": "date",
      "priority": "number",
      "status": "planned|in_progress|achieved"
    }
  },
  {
    "id": "b7",
    "type": "pro",
    "category": "blockers",
    "text": "My blockers",
    "description": "What prevents improvement in my hobbies...",
    "fields": {
      "text": "string",
      "impact_level": "number",
      "related_goals": ["goal_ids"]
    }
  },
  {
    "id": "m7",
    "type": "pro",
    "category": "metrics",
    "text": "My metrics",
    "description": "What can I measure in my hobbies...",
    "metrics": [
      {"name": "Number of hobbies per month", "unit": "pcs", "type": "number"},
      {"name": "Time spent on hobbies per week", "unit": "h", "type": "number"},
      {"name": "Quality of hobby", "unit": "1-10", "type": "scale"}
    ]
  },
  {
    "id": "a7",
    "type": "pro",
    "category": "achievements",
    "text": "My achievements",
    "description": "What I already have today in my hobbies...",
    "fields": {
      "text": "string",
      "date_achieved": "datetime",
      "impact_areas": ["sphere_ids"]
    }
  }
]
```
## 💰 Wealth
```json
[
  {
    "id": "8.1",
    "type": "basic",
    "text": "Financial safety cushion",
    "options": ["Less than 1 month of expenses", "1-3 months", "4-6 months", ">12 months"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "8.2",
    "type": "basic",
    "text": "Investments and savings",
    "options": ["None / <5%", "5-10%", "10-20%", ">20%"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "8.3",
    "type": "basic",
    "text": "Debt load",
    "options": [">80% of income / Very high", "50-80% / High", "20-50% / Moderate", "<20% or no debts / Low"],
    "scores": [4, 3, 2, 1],
    "inverse": true
  },
  {
    "id": "8.4",
    "type": "basic",
    "text": "Budget planning and control",
    "options": ["Spontaneous spending / No control", "Approximate plans / Partial control", "Clear monthly planning / Good control", "Automated system / Full control"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "8.5",
    "type": "basic",
    "text": "Income compliance with your financial goals",
    "options": ["Not enough for basic needs", "Enough, but no savings for goals", "Allows to achieve most goals", "Exceeds all goals, creates surplus"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "8.6",
    "type": "basic",
    "text": "Feeling of financial security",
    "options": ["Very insecure, constant worry", "Rather insecure than secure", "Generally secure and calm", "Completely secure, financial stability"],
    "scores": [1, 2, 3, 4]
  },
  {
    "id": "p8",
    "type": "pro",
    "category": "problems",
    "text": "My problems",
    "description": "What worries me in my wealth...",
    "fields": {
      "text": "string",
      "severity": "number",
      "created_at": "datetime",
      "status": "active|resolved"
    }
  },
  {
    "id": "g8",
    "type": "pro",
    "category": "goals",
    "text": "My goals",
    "description": "What I want to achieve in my wealth...",
    "fields": {
      "text": "string",
      "deadline": "date",
      "priority": "number",
      "status": "planned|in_progress|achieved"
    }
  },
  {
    "id": "b8",
    "type": "pro",
    "category": "blockers",
    "text": "My blockers",
    "description": "What prevents improvement in my wealth...",
    "fields": {
      "text": "string",
      "impact_level": "number",
      "related_goals": ["goal_ids"]
    }
  },
  {
    "id": "m8",
    "type": "pro",
    "category": "metrics",
    "text": "My metrics",
    "description": "What can I measure in my wealth...",
    "metrics": [
      {"name": "Monthly income", "unit": "₽", "type": "number"},
      {"name": "Savings", "unit": "₽", "type": "number"},
      {"name": "Financial stability", "unit": "1-10", "type": "scale"}
    ]
  },
  {
    "id": "a8",
    "type": "pro",
    "category": "achievements",
    "text": "My achievements",
    "description": "What I already have today in my wealth...",
    "fields": {
      "text": "string",
      "date_achieved": "datetime",
      "impact_areas": ["sphere_ids"]
    }
  }
] 
```