import json
import datetime

def lambda_handler(event,context):
    agent=event['agent']
    parameters=event.get('parameters',[])
    function=event['function']
    actionGroup=event['actionGroup']

    def get_time():
        return (datetime.datetime.now()+datetime.timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')

    def add_two_numbers(number_1, number_2):
        return number_1 + number_2

    param_dict={param['name'].lower():int(param['value']) for param in parameters if param['type']=='number' }

    if function == "add_two_numbers":
        number_1=param_dict.get('number_1')
        number_2=param_dict.get('number_2')

        if number_1 is not None and number_2 is not None:
            try:
                number_1=int(number_1)
                number_2=int(number_2)
                result=add_two_numbers(number_1, number_2)
                result_text=f"The sum of {number_1} and {number_2} is {result}"
            except ValueError:
                result_text="Error: Please provide valid numbers for addition."
        else:
            result_text="Error: Please provide both numbers for addition."

        responseBody={
            "TEXT":{
                "body":result_text
            }
        }
    
    elif function == "get_time":
        result=get_time()
        result_text=f"The current time is {result}"
        responseBody={
            "TEXT":{
                "body":result_text
            }
        }

    else:
        result_text="Error: Unknown function"
        responseBody={
            "TEXT":{
                "body":result_text
            }
        }
    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }
    }

    dummy_function_response={
        'response':action_response,
        'messageVersion':event['messageVersion']
    }

    print("Response : {}".format(dummy_function_response))
    return dummy_function_response