with open('backend/api/quotes.py', 'r', encoding='utf-8') as f:
    c = f.read()

target1 = 'from backend.api.notifications import create_notification'
rep1 = 'import logging\nfrom backend.api.notifications import create_notification\n\nlogger = logging.getLogger(__name__)'
if 'logger = logging.getLogger' not in c:
    c = c.replace(target1, rep1, 1)

target2 = 'venue_name=wedding.venue_name or "The Oberoi Udaivilas",'
rep2 = 'venue_name=getattr(wedding, "venue", None) or "The Oberoi Udaivilas",'
c = c.replace(target2, rep2, 1)

assert '—' not in c, 'Em dash detected'

with open('backend/api/quotes.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('backend/api/quotes.py fixed cleanly')

