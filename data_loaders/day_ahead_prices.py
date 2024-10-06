import io
import pandas as pd
import requests
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from datetime import datetime, timezone, timedelta
import uuid
from mage_ai.data_preparation.shared.secrets import get_secret_value
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

@data_loader
def load_data_from_api(*args, **kwargs):
    """
    https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html
    """
    
    url = 'https://web-api.tp.entsoe.eu/api'
    security_token = get_secret_value('entsoe_security_token')
    execution_date = kwargs['execution_date']
    mRID = f"{uuid.uuid4()}"[:15] # Max length is 35
    createdDateTime = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z") # Date/time-stamp of the generation of the request
    DocumentType = "A44" # Day Ahead Price
    NO2 = "10YNO-2--------T" # The market for the price
    Domain = NO2
    fromDateTime = datetime(
        execution_date.year,
        execution_date.month,
        execution_date.day,
        execution_date.hour + 10, # Add 10 hours to pass the next day at 14:00 since day ahead should be available after 13:00
        tzinfo=timezone.utc
      ).isoformat().replace("+00:00", "Z")
    toDateTime = datetime(
        execution_date.year,
        execution_date.month,
        execution_date.day,
        execution_date.hour + 10,
        tzinfo=timezone.utc
      ).isoformat().replace("+00:00", "Z")
    
    data = f'''
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
    '''
    
    response = requests.post(
        url,
        headers={
            'Content-Type': 'application/xml',
            'security_token': security_token
        },
        data=data)
    
    return pd.DataFrame({'request': [data], 'response_status': [response.status_code], 'response_text': [response.text]})


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
    assert (output['response_status'] == 200).all(), 'API did not return status code 200'

"""
Documentations from https://www.reddit.com/r/sweden/comments/r50v12/finns_det_ett_apihemsida_f%C3%B6r_att_h%C3%A4mta_elpriser_i/

returns:
<?xml version="1.0" encoding="utf-8"?>
  <Publication_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3">
    <mRID>d3c8ef8484cf4402a4a6b3281c48542b</mRID>
    <revisionNumber>1</revisionNumber>
    <type>A44</type>
    <sender_MarketParticipant.mRID codingScheme="A01">10X1001A1001A450</sender_MarketParticipant.mRID>
    <sender_MarketParticipant.marketRole.type>A32</sender_MarketParticipant.marketRole.type>
    <receiver_MarketParticipant.mRID codingScheme="A01">10X1001A1001A450</receiver_MarketParticipant.mRID>
    <receiver_MarketParticipant.marketRole.type>A33</receiver_MarketParticipant.marketRole.type>
    <createdDateTime>2024-10-05T16:45:36Z</createdDateTime>
    <period.timeInterval>
      <start>2024-10-05T22:00Z</start>
      <end>2024-10-06T22:00Z</end>
    </period.timeInterval>
      <TimeSeries>
        <mRID>1</mRID>
        <auction.type>A01</auction.type>
        <businessType>A62</businessType>
        <in_Domain.mRID codingScheme="A01">10YNO-2--------T</in_Domain.mRID>
        <out_Domain.mRID codingScheme="A01">10YNO-2--------T</out_Domain.mRID>
        <contract_MarketAgreement.type>A01</contract_MarketAgreement.type>
        <currency_Unit.name>EUR</currency_Unit.name>
        <price_Measure_Unit.name>MWH</price_Measure_Unit.name>
        <curveType>A03</curveType>
          <Period>
            <timeInterval>
              <start>2024-10-05T22:00Z</start>
              <end>2024-10-06T22:00Z</end>
            </timeInterval>
            <resolution>PT60M</resolution>
              <Point>
                <position>1</position>
                 <price.amount>48.44</price.amount>
              </Point>
              <Point>
                <position>2</position>
                 <price.amount>47.54</price.amount>
              </Point>
              <Point>
                <position>3</position>
                 <price.amount>47.59</price.amount>
              </Point>
              <Point>
                <position>4</position>
                 <price.amount>47.49</price.amount>
              </Point>
              <Point>
                <position>5</position>
                 <price.amount>47.69</price.amount>
              </Point>
              <Point>
                <position>6</position>
                 <price.amount>47.73</price.amount>
              </Point>
              <Point>
                <position>8</position>
                 <price.amount>48.22</price.amount>
              </Point>
              <Point>
                <position>9</position>
                 <price.amount>47.24</price.amount>
              </Point>
              <Point>
                <position>10</position>
                 <price.amount>42.68</price.amount>
              </Point>
              <Point>
                <position>11</position>
                 <price.amount>37.14</price.amount>
              </Point>
              <Point>
                <position>12</position>
                 <price.amount>32.25</price.amount>
              </Point>
              <Point>
                <position>13</position>
                 <price.amount>27.36</price.amount>
              </Point>
              <Point>
                <position>14</position>
                 <price.amount>26.22</price.amount>
              </Point>
              <Point>
                <position>15</position>
                 <price.amount>28.76</price.amount>
              </Point>
              <Point>
                <position>16</position>
                 <price.amount>33.71</price.amount>
              </Point>
              <Point>
                <position>17</position>
                 <price.amount>38.45</price.amount>
              </Point>
              <Point>
                <position>18</position>
                 <price.amount>45.16</price.amount>
              </Point>
              <Point>
                <position>19</position>
                 <price.amount>48</price.amount>
              </Point>
              <Point>
                <position>20</position>
                 <price.amount>48.24</price.amount>
              </Point>
              <Point>
                <position>21</position>
                 <price.amount>48.1</price.amount>
              </Point>
              <Point>
                <position>22</position>
                 <price.amount>47.54</price.amount>
              </Point>
              <Point>
                <position>23</position>
                 <price.amount>47.06</price.amount>
              </Point>
              <Point>
                <position>24</position>
                 <price.amount>46.66</price.amount>
              </Point>
          </Period>
          <Period>
            <timeInterval>
              <start>2024-10-04T22:00Z</start>
              <end>2024-10-05T22:00Z</end>
            </timeInterval>
            <resolution>PT60M</resolution>
              <Point>
                <position>1</position>
                 <price.amount>48.74</price.amount>
              </Point>
              <Point>
                <position>2</position>
                 <price.amount>48.44</price.amount>
              </Point>
              <Point>
                <position>3</position>
                 <price.amount>48.38</price.amount>
              </Point>
              <Point>
                <position>4</position>
                 <price.amount>48.31</price.amount>
              </Point>
              <Point>
                <position>5</position>
                 <price.amount>48.27</price.amount>
              </Point>
              <Point>
                <position>6</position>
                 <price.amount>48.22</price.amount>
              </Point>
              <Point>
                <position>7</position>
                 <price.amount>48.38</price.amount>
              </Point>
              <Point>
                <position>8</position>
                 <price.amount>48.45</price.amount>
              </Point>
              <Point>
                <position>9</position>
                 <price.amount>48.85</price.amount>
              </Point>
              <Point>
                <position>10</position>
                 <price.amount>48.92</price.amount>
              </Point>
              <Point>
                <position>11</position>
                 <price.amount>48.94</price.amount>
              </Point>
              <Point>
                <position>12</position>
                 <price.amount>48.83</price.amount>
              </Point>
              <Point>
                <position>13</position>
                 <price.amount>48.05</price.amount>
              </Point>
              <Point>
                <position>14</position>
                 <price.amount>39.23</price.amount>
              </Point>
              <Point>
                <position>15</position>
                 <price.amount>42.22</price.amount>
              </Point>
              <Point>
                <position>16</position>
                 <price.amount>48</price.amount>
              </Point>
              <Point>
                <position>17</position>
                 <price.amount>48.91</price.amount>
              </Point>
              <Point>
                <position>18</position>
                 <price.amount>48.99</price.amount>
              </Point>
              <Point>
                <position>19</position>
                 <price.amount>49.01</price.amount>
              </Point>
              <Point>
                <position>20</position>
                 <price.amount>48.86</price.amount>
              </Point>
              <Point>
                <position>21</position>
                 <price.amount>48.66</price.amount>
              </Point>
              <Point>
                <position>22</position>
                 <price.amount>48.55</price.amount>
              </Point>
              <Point>
                <position>23</position>
                 <price.amount>48.41</price.amount>
              </Point>
              <Point>
                <position>24</position>
                 <price.amount>48.26</price.amount>
              </Point>
          </Period>
      </TimeSeries>
  </Publication_MarketDocument>
  
"""