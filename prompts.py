grammar_prompt = """
You are tasked to generate a set of 10 grammar questions for a TOEIC mock test.

For each question:
1. Create a short business or professional text (1-3 sentences) with a blank space where a grammatical element should go
2. Provide 4 multiple-choice options to fill the blank
3. Include only one correct answer, and it's positioned randomly among the choices
4. Write a detailed explanation for why the correct answer is correct and why the other options are incorrect (in Vietnamese)

The grammar questions should test various grammatical concepts commonly found in TOEIC tests:
- Verb tenses and forms
- Subject-verb agreement
- Modal verbs
- Prepositions
- Articles
- Pronouns
- Conjunctions
- Conditionals
- Passive voice
- Reported speech
- Relative clauses
- Gerunds and infinitives

The contexts should be professional and business-oriented, such as:
- Office communications
- Business meetings
- Professional development
- Work procedures
- Customer service interactions
- Business travel
- Corporate policies

The response should be in JSON format with the following structure:
<json>
{
    "GRAMMAR_DATA": [
        {
            "question": "The candidate __________ resume impressed the entire hiring committee had five years of experience in international sales.",
            "choices": ["who", "whose", "which", "whom"],
            "correct_answer": "whose",
            "explanation": "Trong câu này cần một đại từ quan hệ sở hữu để nối 'candidate' với 'resume'. 'Whose' là đại từ quan hệ sở hữu đúng, dùng để chỉ sự sở hữu của 'candidate' đối với 'resume'. 'Who' dùng cho chủ ngữ người nhưng không thể hiện quan hệ sở hữu. 'Which' dùng cho vật, không phù hợp khi nói về người. 'Whom' là đại từ quan hệ tân ngữ, không dùng để thể hiện sự sở hữu."
        },
        {
            "question": "The CEO decided __________ the expansion plan after reviewing the market forecast.",
            "choices": ["to approve", "approving", "approve", "to approving"],
            "correct_answer": "to approve",
            "explanation": "Sau động từ 'decided', ta dùng động từ nguyên mẫu có 'to' (to-infinitive). 'To approve' là dạng đúng. 'Approving' là dạng gerund (V-ing), không phù hợp sau 'decided'. 'Approve' là nguyên thể nhưng thiếu 'to'. 'To approving' là sai ngữ pháp vì không tồn tại cấu trúc này sau 'decided'."
        },
        {
            "question": "The manager said that the final report __________ before the end of the week.",
            "choices": ["will be submitted", "was submitted", "is submitted", "would be submitted"],
            "correct_answer": "would be submitted",
            "explanation": "Câu này là câu tường thuật (reported speech) với động từ tường thuật 'said' ở thì quá khứ. Vì vậy, mệnh đề sau phải lùi thì theo quy tắc. 'Will be submitted' là thì tương lai đơn, không lùi thì nên sai. 'Would be submitted' là thì tương lai trong quá khứ (future in the past), đúng cấu trúc khi lùi thì từ 'will be submitted'. 'Is submitted' là hiện tại đơn bị động, sai vì không lùi thì. 'Was submitted' là quá khứ đơn bị động, không phù hợp vì nói về hành động tương lai (trước cuối tuần), không phải đã xảy ra trong quá khứ."
        }
    ]
}
</json>
"""

reading_prompt = """
You are tasked to generate a set of 3 reading comprehension passages with questions for a TOEIC mock test.

For each passage:
1. Create an authentic business or professional text (100-200 words) similar to what appears on actual TOEIC tests
2. Write 3 multiple-choice questions related to the passage
3. With each question, there is only one correct answer, and it's positioned randomly among the choices
4. Write a detailed explanation for why the correct answer is correct and why the other options are incorrect (in Vietnamese)
5. Vary the question types to include:
   - Main idea questions
   - Detail questions
   - Inference questions
   - Vocabulary questions
   - Purpose questions
6. Use only standard line breaks \n for formatting
7. Keep all text within valid JSON string format

The passages should cover different professional contexts such as:
- Office communications (emails, memos)
- Business articles
- Product descriptions
- Job advertisements
- Company announcements
- Travel information
- Instructions/procedures

The response should be in JSON format with the following structure:
<json>
{
    "READING_DATA": [
        {
            "passage": "Dear colleagues,\n\nWe are pleased to announce that the annual company retreat will take place from October 15-17 at Mountain View Resort.\n\nAll departments are expected to attend this important team-building event. Please confirm your attendance with your department head by September 30.\n\nTransportation will be provided from the main office at 8:00 AM on October 15. For those who wish to drive separately, parking passes will be available at reception.\n\nThe detailed agenda will be distributed next week.",
            "questions": [
                {
                    "question": "What is the main purpose of this message?",
                    "choices": ["To describe the Mountain View Resort", "To announce a company event", "To request vacation time", "To explain transportation options"],
                    "correct_answer": "To announce a company event",
                    "explanation": "Mục đích chính của văn bản là thông báo về sự kiện công ty thường niên (company retreat), không phải để mô tả khu nghỉ dưỡng, yêu cầu thời gian nghỉ phép hay giải thích các phương tiện đi lại."
                },
                {
                    "question": "By what date must employees confirm their attendance?",
                    "choices": ["September 30", "October 15", "October 17", "Next week"],
                    "correct_answer": "September 30",
                    "explanation": "Theo văn bản, nhân viên phải xác nhận tham dự với trưởng phòng trước ngày 30 tháng 9 (Please confirm your attendance with your department head by September 30)."
                },
                {
                    "question": "What will happen next week according to the message?",
                    "choices": ["The retreat will begin", "Parking passes will be distributed", "The agenda will be shared", "Department heads will meet"],
                    "correct_answer": "The agenda will be shared",
                    "explanation": "Theo thông báo, lịch trình chi tiết sẽ được phân phát vào tuần tới (The detailed agenda will be distributed next week). Không có thông tin nào cho thấy kỳ nghỉ sẽ bắt đầu, vé đậu xe sẽ được phát hoặc trưởng phòng sẽ họp vào tuần tới."
                }
            ]
        }
    ]
}
</json>
"""