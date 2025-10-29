import streamlit as st
import json
from web_search import ResearchAgent

# Page setup
st.set_page_config(page_title="web-searcher", page_icon="M", layout="centered")
st.title("Web Search Agent")
st.caption("You can ask any question — the agent will research in real time and provide answers with cite url.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = ResearchAgent(debug=False)


# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                st.markdown("**🔗 Sources:**")
                for url in msg["sources"]:
                    st.markdown(f"- [{url}]({url})")

# Chat input box
if user_input := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching from websites"):
            result = st.session_state.agent.run(user_input)

        st.markdown(result["answer"])

        if result["sources"]:
            st.markdown("**🔗 Sources:**")
            for url in result["sources"]:
                st.markdown(f"- [{url}]({url})")

        if st.session_state.agent.debug:
            with st.expander("Debug Trace"):
                st.code(json.dumps(result, indent=2), language="json")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result.get("sources", [])
    })

    st.rerun()
