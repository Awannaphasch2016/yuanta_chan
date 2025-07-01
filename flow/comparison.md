### 1. AWS Bedrock Agent (แนวทางที่เรากำลังทำอยู่ตอนนี้)

* **แนวคิด:** ใช้ Amazon Bedrock Agent เป็น "สมอง" หลักที่เข้าใจคำถามของผู้ใช้ และสามารถเรียกใช้ Lambda Functions (Tools) เพื่อไปดึงข้อมูลบริษัทจากแหล่งต่างๆ เช่น Wikipedia, เว็บไซต์บริษัท, หรือฐานข้อมูลทางการเงิน
* **สิ่งที่ต้องวิจัย/นำเสนอ:**
    * **สถาปัตยกรรม (Architecture):** อธิบายว่า Agent จะทำงานร่วมกับ Lambda Functions อย่างไร เพื่อดึงข้อมูลบริษัท
    * **แหล่งข้อมูล:** จะดึงข้อมูลบริษัทจากที่ไหน (เช่น Wikipedia API, Company Website Scraper, Public API for company info)
    * **Lambda Function (Tool) Design:** จะต้องออกแบบ Lambda กี่ตัว แต่ละตัวทำหน้าที่อะไร (เช่น 1 ตัวสำหรับดึงข้อมูลพื้นฐาน, 1 ตัวสำหรับข้อมูลการเงิน) และมี Input/Output Schema อย่างไร
    * **Agent Prompting:** ต้องเขียน Prompt ให้ Agent อย่างไรเพื่อให้เข้าใจว่าเมื่อไหร่ควรใช้ Tool ในการดึงข้อมูลโปรไฟล์บริษัท
* **ตัวอย่างบทสนทนาจริงที่พร้อมสำหรับการนำไปใช้งาน:**

    * **User:** "What does Apple (AAPL) do and how do they make money?"
    * **Chatbot (via Bedrock Agent + Lambda Tool):**
        * *(ภายในระบบ: Agent ตรวจจับคำถามเกี่ยวกับบริษัท Apple และการทำเงิน จึงเรียกใช้ `CompanyProfileTool` (สมมติว่าเป็น Lambda Function ที่เราสร้างขึ้น) โดยส่ง `ticker: "AAPL"` เป็น input)*
        * *(Lambda `CompanyProfileTool` ทำงาน: เรียกใช้ External API เช่น Wikipedia API หรือ Company Info API เพื่อดึงข้อมูลเกี่ยวกับธุรกิจหลักและแหล่งรายได้ของ Apple)*
        * *(Lambda ส่งข้อมูลกลับมาให้ Agent)*
        * *(Agent ประมวลผลและสรุป)*
        * **Chatbot ตอบ:** "Apple Inc. (AAPL) เป็นบริษัทเทคโนโลยีข้ามชาติที่ออกแบบ, พัฒนา, และจำหน่ายอุปกรณ์อิเล็กทรอนิกส์, ซอฟต์แวร์, และบริการออนไลน์ครับ พวกเขาทำเงินหลักๆ จากการขาย iPhone, Mac, iPad รวมถึงอุปกรณ์สวมใส่และเครื่องใช้ในบ้าน (Wearables, Home and Accessories) และยังรวมถึงรายได้จากบริการต่างๆ เช่น App Store, Apple Music, iCloud, และ Apple Pay ครับ"

### 2. Google Conversational AI (Dialogflow/Vertex AI Conversation)

* **แนวคิด:** ใช้แพลตฟอร์ม AI สำหรับการสนทนาของ Google ซึ่งมักจะรวมถึง Dialogflow (สำหรับ Chatbot ทั่วไป) หรือ Vertex AI Conversation (สำหรับโซลูชันระดับองค์กรที่ซับซ้อนขึ้น) เน้นการสร้าง Intent, Entities, และ Fulfillment เพื่อตอบสนองคำถาม
* **สิ่งที่ต้องวิจัย/นำเสนอ:**
    * **วิธีการทำงาน (How it works):** อธิบายแนวคิดของ Intent, Entities, และ Fulfillment Hooks (Webhook) ใน Google Conversational AI
    * **การสร้าง Intent:** จะสร้าง Intent อย่างไรเพื่อจับคำถามเช่น "What does company X do?" หรือ "How does company Y make money?"
    * **Entities:** จะกำหนด Entities (เช่น ชื่อบริษัท/Ticker) อย่างไร
    * **Fulfillment (Webhook):** จะต้องเขียนโค้ดสำหรับ Webhook เพื่อเชื่อมต่อกับแหล่งข้อมูลบริษัท (คล้ายกับ Lambda ของ AWS) และดึงข้อมูลมาตอบ
    * **แหล่งข้อมูล:** จะดึงข้อมูลจากแหล่งใด (เช่น Wikipedia API, Crunchbase API)
* **ตัวอย่างบทสนทนาจริงที่พร้อมสำหรับการนำไปใช้งาน:**

    * **User:** "What does Google (GOOGL) do?"
    * **Chatbot (via Google Conversational AI + Webhook):**
        * *(ภายในระบบ: Dialogflow/Vertex AI Conversation จับคู่คำถามกับ Intent ที่ชื่อ `GetCompanyOverview` และดึง `entity: "Google (GOOGL)"`)*
        * *(Dialogflow เรียกใช้ Webhook ที่เรากำหนดไว้)*
        * *(Webhook ทำงาน: โค้ดใน Webhook เรียก External API เพื่อดึงข้อมูลเกี่ยวกับ Google)*
        * *(Webhook ส่งข้อมูลกลับมาให้ Dialogflow)*
        * **Chatbot ตอบ:** "Google (Alphabet Inc. - GOOGL) เป็นบริษัทเทคโนโลยีที่ให้บริการและผลิตภัณฑ์ที่เกี่ยวข้องกับอินเทอร์เน็ตมากมายครับ รวมถึง Search Engine (Google Search), แพลตฟอร์มวิดีโอ (YouTube), ระบบปฏิบัติการมือถือ (Android), และบริการคลาวด์ (Google Cloud Platform) ครับ"

### 3. n8n (No-code option)

* **แนวคิด:** ใช้แพลตฟอร์ม Automation แบบ No-code/Low-code อย่าง n8n ที่ให้ผู้ใช้สร้าง Workflow การทำงานได้ด้วยการลากและวาง (Drag-and-Drop) และเชื่อมต่อกับบริการต่างๆ โดยไม่ต้องเขียนโค้ดมากนัก เหมาะสำหรับงานที่ต้องการความรวดเร็วและไม่ซับซ้อนมาก
* **สิ่งที่ต้องวิจัย/นำเสนอ:**
    * **วิธีการทำงาน (How it works):** อธิบายแนวคิดของ Nodes, Workflows, และ Trigger ใน n8n
    * **การสร้าง Workflow:** จะสร้าง Workflow ใน n8n อย่างไรเพื่อรับคำถาม, แยกวิเคราะห์ข้อมูล (อาจใช้ Regex หรือ AI Node บางตัว), เรียกใช้ API, และส่งคำตอบกลับ
    * **Nodes ที่ใช้:** จะใช้ Nodes อะไรบ้าง (เช่น Webhook Node สำหรับรับคำถาม, HTTP Request Node สำหรับเรียก API, Set Node สำหรับประมวลผลข้อมูล, Chatbot Integration Node สำหรับตอบกลับ)
    * **แหล่งข้อมูล:** จะดึงข้อมูลจากแหล่งใด (API ที่มีอยู่แล้ว หรือ Public Data Source)
    * **ข้อจำกัด:** อาจมีข้อจำกัดในการประมวลผลภาษาธรรมชาติที่ซับซ้อนเมื่อเทียบกับ AI Agent โดยตรง
* **ตัวอย่างบทสนทนาจริงที่พร้อมสำหรับการนำไปใช้งาน:**

    * **User:** "Tell me about Amazon (AMZN)."
    * **Chatbot (via n8n Workflow):**
        * *(ภายในระบบ: n8n Workflow ถูก Trigger เมื่อได้รับข้อความ)*
        * *(n8n Node ทำการวิเคราะห์ข้อความเพื่อดึง "Amazon" หรือ "AMZN" ออกมา)*
        * *(HTTP Request Node ใน n8n เรียก External API (เช่น Clearbit API หรือ Public Company Info API) ด้วยชื่อบริษัท/Ticker)*
        * *(n8n ประมวลผลข้อมูลที่ได้)*
        * **Chatbot ตอบ:** "Amazon.com, Inc. (AMZN) เป็นบริษัทเทคโนโลยีข้ามชาติสัญชาติอเมริกันที่มุ่งเน้นด้าน E-commerce, Cloud Computing (AWS), Digital Streaming และ Artificial Intelligence ครับ พวกเขาเป็นหนึ่งในบริษัทที่ใหญ่ที่สุดในโลก โดยเป็นที่รู้จักจากแพลตฟอร์มค้าปลีกออนไลน์และบริการ AWS ครับ"