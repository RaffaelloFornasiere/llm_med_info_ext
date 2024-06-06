import json

def map_input(inputs: list = None) -> dict:
    return {'document': inputs[0].output.value['text']}


def map_table_to_json(inputs: list = None) -> list:
    table = inputs[0].output.value
    table = [
        {
            'medication_name': row[0],
            'dosage': row[1] if len(row) > 1 else None,
            'mode': row[2] if len(row) > 2 else None,
            'frequency': row[3] if len(row) > 3 else None,
        }
        for row in table if len(row) > 0 and ''.join(row).strip() != '']
    return table


def map_ita_json_to_json(inputs: list = None):
    json = inputs[0].output.value
    json = [
        {
            'medication_name': row['nome_farmaco'] if 'nome_farmaco' in row else None,
            'dosage': row['dosaggio'] if 'dosaggio' in row else None,
            'mode': row['modalità'] if 'modalità' in row else None,
            'frequency': row['frequenza'] if 'frequenza' in row else None,
        }
        for row in json]
    return json
