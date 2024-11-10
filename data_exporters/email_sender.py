if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
from mage_ai.data_preparation.shared.secrets import get_secret_value
import mailtrap


@data_exporter
def export_data(*data, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    messages = [message for message in data if len(message)]
    token = get_secret_value('mailtrap_token')
    if len(messages):
        # create client and send
        client = mailtrap.MailtrapClient(token=token)
        client.send(mailtrap.Mail(
            sender=mailtrap.Address(email=kwargs['email_from']),
            to=[mailtrap.Address(email=kwargs['email_to'])],
            subject='Alert',
            text=f"""
                {','.join(messages)}
                ---------------------
            """
        ))

    return messages
