import re
def extract_session_id(session_str: str):
    match  = re.search(r"/sessions/(.*?)/contexts/", session_str)

    if match: 
        extracted_string = match.group(1)
        return extracted_string
    

    return ""

if __name__=="__main__":
    print(extract_session_id("projects/my-assistant-qycp/agent/sessions/59658521-573f-3a45-e0d8-35089576e1e3/contexts/ongoing-order"))