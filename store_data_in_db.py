import sqlite3

def InserGraphData(node, packet_size, delay, throughput, num_transaction, datarate):
    conn = sqlite3.connect('throughput_delay_data.db')
    cursor = conn.cursor()
    data_to_insert = (node, packet_size, delay, throughput, num_transaction, datarate)
    cursor.execute('INSERT INTO MultipleDatarate (node, packet_size, delay, throughput, num_transaction, datarate) VALUES (?, ?, ?, ?, ?, ?)', data_to_insert)
   
    conn.commit()
    conn.close()
    
def check_duplicate_data(node, packet_size):
    conn = sqlite3.connect('throughput_delay_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM NetFixTransaction WHERE node = ? AND packet_size = ?', (node, packet_size))
    result = cursor.fetchone()
    
    conn.close()
    
    return result is not None