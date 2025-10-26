document.getElementById('filterBtn').addEventListener('click', async () => {
    let dateFilter = document.getElementById('dateFilter').value;
    if (!dateFilter) {
        alert('Please select a date');
        return;
    }
    await loadRecords(dateFilter);
});

document.getElementById('clearFilter').addEventListener('click', async () => {
    document.getElementById('dateFilter').value = '';
    await loadRecords();
});

async function loadRecords(date = null) {
    try {
        let url = '/api/records';
        if (date) {
            url += '?date=' + date;
        }
        
        let response = await fetch(url);
        let data = await response.json();
        
        if (data.success) {
            let tbody = document.getElementById('recordsBody');
            tbody.innerHTML = '';
            
            if (data.records.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="no-data">No records found</td></tr>';
            } else {
                data.records.forEach(record => {
                    let row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${record.emp_id}</td>
                        <td>${record.name}</td>
                        <td>${record.date}</td>
                        <td>${record.check_in_time || '-'}</td>
                        <td>${record.check_out_time || '-'}</td>
                        <td><span class="status-badge status-${record.status}">${record.status}</span></td>
                    `;
                });
            }
        }
    } catch (err) {
        console.error('Error loading records:', err);
    }
}
