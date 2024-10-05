import io
import pandas as pd
import requests
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from datetime import datetime
import uuid
from mage_ai.data_preparation.shared.secrets import get_secret_value

@data_loader
def load_data_from_api(*args, **kwargs):
    """
    https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html
    """
    
    url = 'https://web-api.tp.entsoe.eu/api'
    security_token = get_secret_value('entsoe_security_token')
    execution_date = datetime.fromisoformat(kwargs['execution_date'])
    mRID = uuid()
    createdDateTime = datetime.utcnow().isoformat() # Date/time-stamp of the generation of the request
    DocumentType = "A44" # Day Ahead Price
    SE3 = "10Y1001A1001A46L" # The market for the price, Sweden SE3 = 10Y1001A1001A46L
    NO2 = "10YNO-2--------T"
    Domain = NO2
    fromDateTime = datetime(execution_date.year, execution_date.month, execution_date.day).isoformat()
    toDateTime = datetime(execution_date.year, execution_date.month, execution_date.day, 23).isoformat() # The period from/to, to get a full day add from 00:00 to 23:00
    if True:
        print(mRID)
        return None
    response = requests.post(
        url,
        header={
            'Content-Type': 'application/xml'
            'security_token': security_token
        },
        data=f'''
<StatusRequest_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-5:statusrequestdocument:4:0">
    <mRID>{mRID}</mRID>
    <type>A59</type>
    <sender_MarketParticipant.mRID codingScheme="A01">10X1001A1001A450</sender_MarketParticipant.mRID>
    <sender_MarketParticipant.marketRole.type>A07</sender_MarketParticipant.marketRole.type>
    <receiver_MarketParticipant.mRID codingScheme="A01">10X1001A1001A450</receiver_MarketParticipant.mRID>
    <receiver_MarketParticipant.marketRole.type>A32</receiver_MarketParticipant.marketRole.type>
    <createdDateTime>{createdDateTime}</createdDateTime>
    <AttributeInstanceComponent>
        <attribute>DocumentType</attribute>
        <attributeValue>{DocumentType}</attributeValue>
    </AttributeInstanceComponent>
    <AttributeInstanceComponent>
        <attribute>In_Domain</attribute>
        <attributeValue>{Domain}</attributeValue>
    </AttributeInstanceComponent>
    <AttributeInstanceComponent>
        <attribute>Out_Domain</attribute>
        <attributeValue>{Domain}</attributeValue>
    </AttributeInstanceComponent>
    <AttributeInstanceComponent>
        <attribute>TimeInterval</attribute>
        <attributeValue>{fromDateTime}/{toDateTime}</attributeValue>
    </AttributeInstanceComponent>
</StatusRequest_MarketDocument>
    ''')

    print(response.status_code)
    return pd.read_csv(io.StringIO(response.text), sep=',')


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'


"""
Documentations from https://www.reddit.com/r/sweden/comments/r50v12/finns_det_ett_apihemsida_f%C3%B6r_att_h%C3%A4mta_elpriser_i/
"""