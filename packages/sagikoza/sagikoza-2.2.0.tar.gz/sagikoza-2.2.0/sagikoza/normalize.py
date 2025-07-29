from typing import Any, Dict, List
import unicodedata
import re

def normalize_accounts(account: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize account data by generating unique identifiers.
    
    Args:
        accounts (Dict[str, Any]): Dictionary of account data.
        
    Returns:
        List[Dict[str, Any]]: List of accounts with unique identifiers.
    """
    if 'error' in account:
        return []  # Skip accounts with errors

    # Generate a unique identifier for the account
    for field in ['name', 'name_alias']:
        if field in account and isinstance(account[field], str):
            # 濁点と半濁点を合成可能な濁点と半濁点に標準化
            account[field] = account[field].replace('\u309B', '\u3099').replace('\u309C', '\u309A')
            # 長音を標準化
            account[field] = re.sub(r'[-˗ᅳ᭸‐‑‒–—―⁃⁻−▬─━➖ーㅡ﹘﹣－ｰ𐄐𐆑]', 'ー', account[field])
            # 括弧以外の文字列を標準化
            account[field] = unicodedata.normalize('NFKC', account[field]).replace('(', '（').replace(')', '）')
    
    # nameフィールドが「半角英数スペース (全角カナ半角スペース３文字以上)」の場合、分割する
    if 'name' in account and isinstance(account['name'], str):
        m = re.match(r'^([A-Za-z0-9 ]+)\s*\（([\u30A0-\u30FF\s]{3,})\）$', account['name'])
        if m:
            account['name'] = m.group(2).strip()
            account['name_alias'] = m.group(1).strip()
    

    for date_field in ['notice_date', 'suspend_date', 'delete_date']:
        if date_field in account and isinstance(account[date_field], str):
            # 例: '2024年6月5日' -> '2024-06-05'
            try:
                m = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', account[date_field])
                if m:
                    year, month, day = m.groups()
                    account[date_field] = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
            except Exception:
                pass

    return [account]