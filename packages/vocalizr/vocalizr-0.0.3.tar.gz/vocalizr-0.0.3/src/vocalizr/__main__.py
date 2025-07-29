from gradio import Blocks

from vocalizr import DEBUG, SERVER_NAME, SERVER_PORT
from vocalizr.gui import app_block


def main() -> None:
    """Launch the Gradio voice generation web application."""
    app: Blocks = app_block()
    app.queue(api_open=True).launch(
        server_name=SERVER_NAME,
        server_port=SERVER_PORT,
        debug=DEBUG,
        mcp_server=True,
        show_api=True,
        enable_monitoring=True,
        show_error=True,
        pwa=True,
    )


if __name__ == "__main__":
    main()
