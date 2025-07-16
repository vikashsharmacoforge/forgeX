from shiny import App, ui, render, reactive, Inputs, Outputs, Session, run_app
import requests
import json
import sys
import os
import uuid

sys.path.append(os.path.abspath("../src/utils"))
from stm_context_manager import store_messages, get_conversation

INITIAL_STATE = 'START'

css_styles = """
<style>
        .sticky-top-nav {
            position: sticky;
            top: 0;
            z-index: 1000;
            transition: top 0.3s;
        }
        .hide-nav {
            top: -70px !important;
        }
        .main-content {
            padding-top: 70px;
        }
        .agent-bar {
            background: #1976d2 !important;
            color: #fff !important;
        }
        .agent-bar .btn, .agent-bar .btn:active, .agent-bar .btn:focus, .agent-bar .btn:hover {
            color: #fff !important;
        }
        .bg-primary .btn, .bg-primary .btn:active, .bg-primary .btn:focus, .bg-primary .btn:hover {
            color: #fff !important;
        }
</style>
"""

# --- UI Layout ---
app_ui = ui.page_fluid(
    ui.HTML(css_styles),
    ui.div(
        ui.row(
            ui.column(
                2,
                ui.div(
                    # ui.img(src=r"D:\OneDrive - Coforge Limited\Desktop\ForgeX\forgexgit\forgeX\img\logo.png", style="height:40px;vertical-align:middle;margin-right:10px;", alt="Logo"),
                    class_="p-2 fw-bold fs-4"
                )
            ),
            ui.column(8, ui.div()),  # Spacer
            ui.column(2,
                ui.div(
                    ui.input_action_button("history_btn", "Session History", class_="mx-2"),
                    ui.input_action_button("notif_btn", "Agent Messages", class_="mx-2"),
                    ui.input_action_button("memory_btn", "Session State", class_="mx-2"),
                    class_="d-flex justify-content-end align-items-center"
                )
            ),
            class_="bg-primary text-white py-2",
        ),
        class_="sticky-top-nav",
        id="topNavBar"
    ),

    # Add JS to hide nav bar on scroll
    ui.tags.script("""
        let lastScrollTop = 0;
        window.addEventListener('scroll', function(){
            let nav = document.getElementById('topNavBar');
            let st = window.pageYOffset || document.documentElement.scrollTop;
            if(st > lastScrollTop && st > 70){
                nav.classList.add('hide-nav');
            } else {
                nav.classList.remove('hide-nav');
            }
            lastScrollTop = st <= 0 ? 0 : st;
        }, false);
    """),
    # Main Content starts below nav bar
    ui.div(
        ui.row(
            # Sidebar
            ui.column(2,
                ui.div(
                    ui.h5("Side Panel"),
                    ui.input_file("file_upload", "Upload File"),
                    class_="bg-light p-3 vh-100"
                ),
                style="padding-top:0;"
            ),
            # Main Area
            ui.column(10,
                ui.div(
                    # Agent Bar
                    ui.div(
                        ui.row(
                            *[
                                ui.column(2, ui.input_action_button(f"agent{i}_btn", f"Agent {i}", class_="w-100"))
                                for i in range(1, 6)
                            ],
                            class_="g-2"
                        ),
                        class_="agent-bar px-3 py-2 mb-3",
                        style="margin-top:0;"
                    ),
                    # Output Canvas with chat box
                    ui.div(
                        ui.div(
                            ui.output_ui("main_canvas"),
                            style="height:60vh;border:2px dashed #bbb;background:#fafafa;display:flex;justify-content:center;font-size:1.2rem;color:#888;flex-direction:column;overflow-y:auto;",
                        ),
                        ui.div(
                            ui.input_text("chat_input", label=None, placeholder="Type your message...", width="80%"),
                            ui.input_action_button("send_btn", "Send", class_="mx-2"),
                            style="display:flex;justify-content:center;align-items:center;margin-top:1rem;"
                        ),
                        style="width:100%;"
                    ),
                    # Add to UI (for testing)
                    ui.input_action_button("test_btn", "Test Message"),
                ),
            ),
        ),
        class_="main-content"
    ),
)

# --- Server Logic ---
def server(input: Inputs, output: Outputs, session: Session):
    state = reactive.Value(INITIAL_STATE)
    session_uuid = reactive.Value(str(uuid.uuid4()))
    chat_messages = reactive.Value([])

    @output
    @render.ui
    def main_canvas():
        # Display chat messages in the output canvas
        messages = chat_messages.get()
        if not messages:
            return ui.p("Output will appear here.")
        html = ""
        for m in messages:
            role = m.get("role")
            content = m.get("content")
            html += f'<div style="margin-bottom:10px;"><b>{role}:</b><br>{content}</div>'
        return ui.HTML(html)

    @reactive.effect
    @reactive.event(input.send_btn)
    async def _():
        user_input = input.chat_input()
        if not user_input:
            return
        # msgs = chat_messages.get()
        # msgs.append({"role": "user", "content": user_input})
        # chat_messages.set(msgs)
        chat_messages.set(chat_messages.get()+[{"role": "user", "content": user_input}])
        ui.update_text("chat_input", value="")  # Clear input box

        # Store message and get assistant response
        try:
            await store_messages(session_uuid.get(), state.get(), {"role": "user", "content": user_input})
        except Exception as e:
            # msgs.append({"role": "assistant", "content": f"Error storing messages: {e}"})
            # chat_messages.set(msgs)
            chat_messages.set(chat_messages.get()+[{"role": "assistant", "content": f"Error storing messages: {e}"}])
            return

        response = requests.post(
            "http://localhost:5678/webhook/77ab886c-4239-4cc7-8e1d-00e20c26a4b8",
            json={"data": {"messages": [{"role": "user", "content": user_input}], "state": state.get(), "_uuid": session_uuid.get()}},
        )
        if response.status_code == 200 and response.text.strip():
            try:
                response_data = response.json()
                if 'stdout' in response_data:
                    try:
                        stdout_data = json.loads(response_data['stdout'])
                        if 'response' in stdout_data:
                            state.set(stdout_data['response'].get("state", str))
                        assistant_msg = await get_conversation(session_uuid.get(), state.get())
                        assistant_msg = assistant_msg.get("response", [])
                        if isinstance(assistant_msg, list) and assistant_msg:
                            last_msg = assistant_msg[-1]
                            if isinstance(last_msg, dict) and last_msg.get("role") == "assistant":
                                # msgs.append(last_msg)
                                print("Asistant message (dict):",last_msg)
                                chat_messages.set(chat_messages.get()+[last_msg])
                            else:
                                # msgs.append({"role": "assistant", "content": str(last_msg)})
                                print("Assistant message:",last_msg)
                                chat_messages.set(chat_messages.get()+[{"role": "assistant", "content": str(last_msg)}])
                        else:
                            # msgs.append({"role": "assistant", "content": str(assistant_msg)})
                            print("Assistant response:",assistant_msg)
                            chat_messages.set(chat_messages.get()+[{"role": "assistant", "content": str(assistant_msg)}])
                        # chat_messages.set(msgs)
                    except json.JSONDecodeError as e:
                        # msgs.append({"role": "assistant", "content": f"Error parsing stdout JSON: {e}"})
                        chat_messages.set(chat_messages.get()+[{"role": "assistant", "content": f"Error parsing stdout JSON: {e}"}])
            except Exception as e:
                # msgs.append({"role": "assistant", "content": f"Error decoding response JSON: {e}"})
                chat_messages.set(chat_messages()+[{"role": "assistant", "content": f"Error decoding response JSON: {e}"}])
        else:
            # msgs.append({"role": "assistant", "content": f"Error: {response.status_code} - {response.text}"})
            chat_messages.set(chat_messages()+[{"role": "assistant", "content": f"Error: {response.status_code} - {response.text}"}])

    # Add to server
    @reactive.effect
    @reactive.event(input.test_btn)
    def _():
        msgs = chat_messages.get()
        msgs.append({"role": "assistant", "content": "Test message"})
        chat_messages.set(msgs)
        print(chat_messages.get())

app = App(app_ui, server)

if __name__ == "__main__":
    print("Starting MCP Tool Explorer app...")
    run_app(app, port=8001, launch_browser=True)