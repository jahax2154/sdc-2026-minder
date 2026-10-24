"""Scope the approved page styles so they cannot change the shared shell."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[3]

def scope_css(css, scope):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    def rules(text):
        result, pos = [], 0
        while pos < len(text):
            start = text.find('{', pos)
            if start < 0: break
            selector = text[pos:start].strip()
            depth, end, quote = 1, start + 1, None
            while depth:
                c = text[end]
                if quote:
                    if c == quote and text[end-1] != '\\': quote = None
                elif c in "\"'": quote = c
                elif c == '{': depth += 1
                elif c == '}': depth -= 1
                end += 1
            body = text[start+1:end-1]
            if selector.startswith(('@media', '@supports')):
                result.append(selector + '{' + rules(body) + '}')
            elif selector.startswith('@'):
                # Animation names are prefixed to avoid collisions outside these pages.
                result.append(selector.replace('arrive', 'approved-arrive') + '{' + body + '}')
            else:
                selectors = []
                for value in selector.split(','):
                    value = value.strip()
                    if value in (':root', 'html', 'body', 'main', '.page-main'):
                        selectors.append(scope)
                    else:
                        selectors.append(scope + ' ' + value)
                result.append(','.join(selectors) + '{' + body.replace('animation:arrive', 'animation:approved-arrive') + '}')
            pos = end
        return '\n'.join(result)
    return rules(css)

explore = ROOT/'docs/minder-approved-product-designs/explore-v1/assets/styles.css'
profile = ROOT/'docs/minder-approved-product-designs/profile-v2/minder-user-profile-prototype-v2.html'
profile_css = re.search(r'<style>(.*?)</style>', profile.read_text(), re.S).group(1)
out = ROOT/'apps/frontend-product/assets/approved-pages.css'
out.write_text('/* Generated from committed approved designs; run tools/import_approved_styles.py. */\n' + scope_css(explore.read_text(), '.morning-explore') + '\n' + scope_css(profile_css, '.morning-profile') + '\n')

# Home uses only scoped body components; its standalone shell never replaces F shell.
home = ROOT/'docs/Minder_Home_Package/assets/styles.css'
(ROOT/'apps/frontend-product/assets/approved-home.css').write_text('/* Generated from docs/Minder_Home_Package/assets/styles.css. */\n'+scope_css(home.read_text(), '.morning-home')+'\n')
