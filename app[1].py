
import streamlit as st
from io import BytesIO
import requests
from pypdf import PdfReader
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Work Pilot", page_icon="🚀", layout="wide")

if "reminders" not in st.session_state:
    st.session_state.reminders = []
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

st.markdown("""
<style>
.block-container {padding-top: 2rem;}
.hero {
    padding: 24px;
    border-radius: 18px;
    background: linear-gradient(135deg, #172554, #0f766e);
    color: white;
    margin-bottom: 20px;
}
.hero h1 {font-size: 46px; margin: 0;}
.hero p {font-size: 18px; margin-top: 8px;}
.card {
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #d9dee8;
    background: rgba(255,255,255,0.03);
    min-height: 130px;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🚀 Work Pilot")
st.sidebar.caption("Smart academic work assistant")
page = st.sidebar.radio(
    "Menu",
    ["Home", "File Search", "Web → PDF", "Reminders",
     "Recorded Class", "Video Tracker", "Test Maker", "AI Assistant"]
)

if page == "Home":
    st.markdown("""
    <div class="hero">
      <h1>🚀 Work Pilot</h1>
      <p>Your smart academic work assistant for faculty.</p>
    </div>
    """, unsafe_allow_html=True)
    st.success("Manage teaching resources, classes, reminders and tests in one place.")
    cols = st.columns(3)
    cards = [
        ("📂 File Search", "Upload PDFs and search inside their content."),
        ("🌐 Web → PDF", "Create a study PDF from an online topic summary."),
        ("⏰ Reminders", "Create and view academic task reminders."),
        ("🎥 Recorded Class", "Upload and play a recorded lecture."),
        ("📊 Video Tracker", "Track student video progress."),
        ("📝 Test Maker", "Create 4-option tests with partial-credit levels."),
    ]
    for i, (title, desc) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(f'<div class="card"><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
    st.info("Demo tip: start with File Search, then Test Maker and Recorded Class.")

elif page == "File Search":
    st.title("📂 File Search")
    st.write("Upload PDFs and search the actual text inside them.")
    files = st.file_uploader("Upload teaching PDFs", type=["pdf"], accept_multiple_files=True)
    query = st.text_input("Search inside your files", placeholder="Example: software process model")
    if files:
        for f in files:
            if not any(d["name"] == f.name for d in st.session_state.uploaded_docs):
                try:
                    reader = PdfReader(BytesIO(f.getvalue()))
                    text = "\n".join((p.extract_text() or "") for p in reader.pages)
                    st.session_state.uploaded_docs.append({"name": f.name, "text": text, "bytes": f.getvalue()})
                except Exception:
                    pass
    if st.session_state.uploaded_docs:
        st.subheader("Uploaded files")
        for d in st.session_state.uploaded_docs:
            st.write(f"📄 **{d['name']}**")
            if query.strip():
                q = query.lower()
                pos = d["text"].lower().find(q)
                if pos >= 0:
                    start = max(0, pos - 180)
                    end = min(len(d["text"]), pos + len(q) + 420)
                    st.success("Match found")
                    st.write(d["text"][start:end].replace("\n", " "))
                else:
                    st.caption("No text match in this file.")
            st.download_button("Download", d["bytes"], d["name"], key=f"dl_{d['name']}")
    else:
        st.info("Upload a PDF to begin.")

elif page == "Web → PDF":
    st.title("🌐 Web → PDF")
    st.write("Enter a topic. Work Pilot fetches an online Wikipedia summary and turns it into a PDF.")
    topic = st.text_input("Topic", placeholder="Artificial Intelligence")
    if st.button("Create PDF", type="primary"):
        if not topic.strip():
            st.warning("Enter a topic first.")
        else:
            with st.spinner("Fetching online study material..."):
                try:
                    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(topic.strip().replace(" ", "_"))
                    r = requests.get(url, timeout=10)
                    if r.status_code != 200:
                        st.error("I couldn't find that topic online. Try a simpler topic name.")
                    else:
                        data = r.json()
                        title = data.get("title", topic)
                        extract = data.get("extract", "No summary was returned.")
                        pdf = BytesIO()
                        c = canvas.Canvas(pdf)
                        c.setTitle(f"Work Pilot - {title}")
                        c.setFont("Helvetica-Bold", 18)
                        c.drawString(50, 800, f"Work Pilot - {title}")
                        c.setFont("Helvetica", 10)
                        y = 770
                        for sentence in extract.split(". "):
                            sentence = sentence.strip()
                            if not sentence:
                                continue
                            for start in range(0, len(sentence), 95):
                                c.drawString(50, y, sentence[start:start+95])
                                y -= 15
                                if y < 60:
                                    c.showPage()
                                    y = 800
                                    c.setFont("Helvetica", 10)
                        c.save()
                        pdf.seek(0)
                        st.success("PDF created!")
                        st.download_button("📥 Download PDF", pdf.getvalue(), "WorkPilot_Study_Material.pdf", "application/pdf")
                        st.write(extract)
                except Exception as e:
                    st.error(f"Could not create the PDF: {e}")

elif page == "Reminders":
    st.title("⏰ Reminders")
    task = st.text_input("Task", placeholder="Prepare DBMS PPT")
    day = st.date_input("Date")
    time = st.time_input("Time")
    if st.button("Add Reminder", type="primary"):
        if task.strip():
            st.session_state.reminders.append({"task": task.strip(), "date": str(day), "time": str(time)})
            st.success("Reminder added!")
        else:
            st.warning("Enter a task.")
    st.subheader("My reminders")
    if not st.session_state.reminders:
        st.info("No reminders yet.")
    else:
        for i, r in enumerate(st.session_state.reminders, 1):
            st.write(f"**{i}. {r['task']}** — {r['date']} at {r['time']}")

elif page == "Recorded Class":
    st.title("🎥 Recorded Class")
    st.write("Upload a lecture video and play it for students.")
    title = st.text_input("Class title", placeholder="DBMS Unit 1")
    video = st.file_uploader("Upload video", type=["mp4", "mov", "webm"])
    if video:
        st.success(f"{title or 'Recorded class'} uploaded successfully.")
        st.video(video)

elif page == "Video Tracker":
    st.title("📊 Video Tracker")
    student = st.text_input("Student name", placeholder="Student name")
    progress = st.slider("Video watched", 0, 100, 50)
    st.progress(progress / 100)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Progress", f"{progress}%")
    with c2:
        st.metric("Status", "Completed" if progress == 100 else "In Progress")
    if progress == 100:
        st.success(f"{student or 'Student'} completed the lecture!")
    elif progress >= 50:
        st.info(f"{student or 'Student'} has watched more than half.")
    else:
        st.warning(f"{student or 'Student'} needs to watch more.")

elif page == "Test Maker":
    st.title("📝 Test Maker")
    st.write("Create a question with four options and partial-credit levels.")
    q = st.text_area("Question", placeholder="What is Python?")
    a = st.text_input("Option A — 100%")
    b = st.text_input("Option B — 75%")
    c = st.text_input("Option C — 50%")
    d = st.text_input("Option D — 25%")
    if st.button("Create Test", type="primary"):
        if all(x.strip() for x in [q, a, b, c, d]):
            st.success("Test question created!")
            st.markdown(f"### {q}")
            st.write(f"**A.** {a} — 100%")
            st.write(f"**B.** {b} — 75%")
            st.write(f"**C.** {c} — 50%")
            st.write(f"**D.** {d} — 25%")
        else:
            st.warning("Fill the question and all four options.")

elif page == "AI Assistant":
    st.title("🤖 AI Assistant")
    st.write("A simple academic assistant for demo use.")
    prompt = st.text_area("What do you need?", placeholder="Create 5 questions about DBMS")
    if st.button("Ask Work Pilot", type="primary"):
        if not prompt.strip():
            st.warning("Enter a request.")
        else:
            p = prompt.lower()
            if "question" in p or "quiz" in p or "test" in p:
                st.write("### Sample questions")
                st.write("1. What is DBMS?")
                st.write("2. What is a primary key?")
                st.write("3. What is normalization?")
                st.write("4. What is SQL?")
                st.write("5. What is a foreign key?")
            elif "ppt" in p or "presentation" in p:
                st.write("### PPT outline")
                st.write("1. Introduction\n2. Key concepts\n3. Examples\n4. Applications\n5. Advantages\n6. Conclusion")
            else:
                st.info("Try asking Work Pilot to create test questions or a PPT outline.")
