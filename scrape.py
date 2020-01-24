from unicodedata import normalize


def is_goop_post(url):
    title = url.split('/')[-2]
    try:
        int(title)
        return False
    except Exception as e:
        return title


def scrape_page(url, selector, session, site):
    title_selector, body_selector, quit_after, skip_text, remove, render = selector

    r = session.get(url)
    if render:
        r.html.render()
    if site == 'goop':
        title = is_goop_post(url)
        if not title:
            raise ValueError
    else:
        if isinstance(title_selector, int):
            title = url[title_selector:]
        else:
            title = r.html.find(title_selector)[0].text.split('|')[0].strip().replace(' ', '_')

    body = r.html.find(body_selector)
    if quit_after:
        content_text = []
        for c in body:
            if c.text:
                if not c.text.startswith(quit_after):
                    content_text.append(c.text)
                else:
                    break
        body = content_text

    body = (' ').join([c.text for c in body])
    body = normalize('NFKD', body)
    if skip_text:
        for skip in skip_text:
            body = '.'.join([line for line in body.split('.') if skip.lower() not in line.lower()])
    if remove:
        for r in remove:
            body = body.replace(r, '',)
    return title, body
