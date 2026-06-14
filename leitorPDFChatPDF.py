import requests

caminho_arquivo = r"C:\rpa\contabilidade\Notas Representantes\PDFs\BOLLES.pdf"
files = [
    ('file', ('file', open(caminho_arquivo, 'rb'), 'application/octet-stream'))
]
headers = {
    'x-api-key': 'sec_gl1ZYlz9EoW1w6HbE1FBecFauXDNSGiG'
}

response = requests.post(
    'https://api.chatpdf.com/v1/sources/add-file', headers=headers, files=files)

if response.status_code == 200:
    source_id = response.json()['sourceId']

    data = {
        'sourceId': str(source_id),
        'messages': [
            {
                'role': "user",
                'content': "Me retorne, tendo como nome da informação os seguintes dados da nota fiscal: o CNPJ do tomador, o CNPJ do emitente, o valor total da NF (em formato PT-BR), a alíquota do IR (em formato PT-BR), o valor do IR (em formato PT-BR), a alíquota do ISS (em formato PT-BR), o valor do ISS (em formato PT-BR) e o valor líquido da NF (em formato PT-BR)"
            }
        ]
    }

    response = requests.post(
        'https://api.chatpdf.com/v1/chats/message', headers=headers, json=data)

    if response.status_code == 200:
        print('Result:', response.json()['content'])
    else:
        print('Status:', response.status_code)
        print('Error:', response.text)