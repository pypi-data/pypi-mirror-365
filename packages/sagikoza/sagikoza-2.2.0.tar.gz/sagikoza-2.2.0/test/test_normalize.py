from bs4 import BeautifulSoup
import pytest
from unittest.mock import patch

from sagikoza import core

@pytest.fixture
def k_pubstype_01_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_01_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_normalize_pubstype_01_detail_1(k_pubstype_01_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_01_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2505-9900-0335",
            "pn": "375438",
            "p_id": "03",
            "re": "0",
            "referer": '0'
        }
        accounts = core._pubstype_detail(subject)
        
        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': 'd06beb36cbb0a609e8942a7f09c91a74819a9013368bc8b072abbce66cb42ede',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'branch_name': '二二八', 
            'branch_code': '228', 
            'account_type': '普通預金', 
            'account': '3084648', 
            'name': 'リードバンク（ド', 
            'amount': '853305', 
            'effective_from': '2025年6月3日 0時', 
            'effective_to': '2025年8月4日 15時', 
            'effective_method': '所定の届出書を提出（詳細は照会先へご連絡下さい）', 
            'payment_period': '２０２４年１０月', 
            'suspend_date': '2024-10-21', 
            'notes': '', 
            'branch_code_jpb': '12250',
            'account_jpb': '30846481',
            'name_alias': 'リードバンク 合同会社',
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-9900-0335', 
            'pn': '375438', 
            'p_id': '03', 
            're': '0', 
            'referer': '0'
        }
        assert core.normalize_accounts(accounts[0])[0] == expected

        # 青木信用金庫ケースの確認
        expected = {
            'uid': 'ba2185b8eaa17003594792efb318cfbea291d89e8f735612b1b045fff7060878',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': '青木信用金庫', 
            'branch_name': '越谷支店', 
            'branch_code': '014', 
            'account_type': '普通預金', 
            'account': '5032277', 
            'name': 'カ）パレット', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '２０２４年１０月', 
            'suspend_date': '', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-9900-0335', 
            'pn': '375438', 
            'p_id': '03', 
            're': '0', 
            'referer': '0'
        }
        assert core.normalize_accounts(accounts[1])[0] == expected

        # 京葉銀行ケースの確認
        expected = {
            'uid': '790ab5c511422a81b0558fb964d7611ec56a8a445246b1dca8c6ef41f9d75462',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': '京葉銀行', 
            'branch_name': '鎌取支店', 
            'branch_code': '418', 
            'account_type': '普通預金', 
            'account': '5569011', 
            'name': 'ド）シュガーラッシュ', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '２０２４年１０月', 
            'suspend_date': '', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-9900-0335', 
            'pn': '375438', 
            'p_id': '03', 
            're': '0', 
            'referer': '0'
        }
        assert core.normalize_accounts(accounts[2])[0] == expected

@pytest.fixture
def k_pubstype_01_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_01_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_01_detail_2(k_pubstype_01_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_01_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2506-0001-0894",
            "pn": "375331",
            "p_id": "03",
            "re": "0",
            "referer": '1'
        }
        accounts = core._pubstype_detail(subject)
        
        # みずほ銀行（外国人）ケースの確認
        expected = {
            'uid': '69a94fde4b4a74f02c26e396ca8e5f6bce66150b671be386a156f820eefcdb0b',
            'role': '対象預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '山形支店', 
            'branch_code': '728', 
            'account_type': '普通預金', 
            'account': '3056028', 
            'name': 'フアン ヴアン マイン', 
            'amount': '2599', 
            'effective_from': '2025年6月17日 0時', 
            'effective_to': '2025年8月18日 15時', 
            'effective_method': '所定の届出書を提出（詳細は照会先へご連絡下さい）', 
            'payment_period': '2024年08月頃', 
            'suspend_date': '2024-08-16', 
            'notes': '', 
            'name_alias': 'PHAM VAN MANH',
            'form': 'k_pubstype_01_detail.php', 
            'no': '2506-0001-0894', 
            'pn': '375331', 
            'p_id': '03', 
            're': '0', 
            'referer': '1'
        }
        assert core.normalize_accounts(accounts[0])[0] == expected

@pytest.fixture
def k_pubstype_04_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_04_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_04_detail_1(k_pubstype_04_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_04_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_04_detail.php",
            "no": "2503-9900-0475",
            "pn": "368470",
            "p_id": "05",
            "re": "0",
            "referer": '0'
        }
        accounts = core._pubstype_detail(subject)
        
        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': '2e7ece3550b9b3036f0a6e3680a7cc6c1b0d2e06a10741ef760f516b96c6a004',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'branch_name': '五一八', 
            'branch_code': '518', 
            'account_type': '普通預金', 
            'account': '6211644', 
            'name': 'フャン ティ カイン リー', 
            'amount': '602827', 
            'notice_date': '2025-05-01',
            'notes': '法第六条第一項（権利行使の届出等あり）',
            'branch_code_jpb': '15150',
            'account_jpb': '62116441',
            'name_alias': 'PHAN THI KHANH LY',
            "form": "k_pubstype_04_detail.php",
            "no": "2503-9900-0475",
            "pn": "368470",
            "p_id": "05",
            "re": "0",
            "referer": '0'
        }
        assert core.normalize_accounts(accounts[0])[0] == expected

@pytest.fixture
def k_pubstype_04_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_04_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_04_detail_2(k_pubstype_04_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_04_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_04_detail.php",
            "no": "2507-0310-0051",
            "pn": "372840",
            "p_id": "05",
            "re": "0",
            "referer": '0'
        }
        accounts = core._pubstype_detail(subject)
        
        # ＧＭＯあおぞらネット銀行ケースの確認
        expected = {
            'uid': '7284c8a2a78d09c216928ba2b6a747bd14d1b3d5d72b3f51102d24ec58a58a4b',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ＧＭＯあおぞらネット銀行', 
            'branch_name': 'フリー支店', 
            'branch_code': '125', 
            'account_type': '普通預金', 
            'account': '1121426', 
            'name': 'カ）フアイナンシヤルラグジユアリー', 
            'amount': '8676', 
            'notice_date': '2025-07-01',
            'notes': '法第六条第一項（権利行使の届出等あり）',
            "form": "k_pubstype_04_detail.php",
            "no": "2507-0310-0051",
            "pn": "372840",
            "p_id": "05",
            "re": "0",
            "referer": '0'
        }
        assert core.normalize_accounts(accounts[0])[0] == expected

@pytest.fixture
def k_pubstype_05_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_05_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_05_detail_1(k_pubstype_05_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_05_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_05_detail.php",
            "no": "2503-9900-0011",
            "pn": "373302",
            "p_id": "07",
            "re": "0",
            "referer": '0'
        }
        accounts = core._pubstype_detail(subject)

        # みずほ銀行ケースの確認
        expected = {
            'uid': 'ff68656c1dfdaf90b4cee00bf3c129cfd67ca71088682b2e605990ad5f02cfd3',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'name': 'ブイ ヴァン ビン', 
            'amount': '773', 
            'notice_date': '2025-05-01',
            'delete_date': '2025-07-01',
            'branch_code_jpb': '19730',
            'account_jpb': '16099061',
            'name_alias': 'BUI VAN BINH',
            "form": "k_pubstype_05_detail.php",
            "no": "2503-9900-0011",
            "pn": "373302",
            "p_id": "07",
            "re": "0",
            "referer": '0'
        }
        assert core.normalize_accounts(accounts[0])[0] == expected

@pytest.fixture
def k_pubstype_05_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_05_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_05_detail_2(k_pubstype_05_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_05_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_05_detail.php",
            "no": "2502-0001-0034",
            "pn": "371209",
            "p_id": "07",
            "re": "0",
            "referer": '0'
        }
        accounts = core._pubstype_detail(subject)

        # みずほ銀行ケースの確認
        expected = {
            'uid': '6e8f140f6eaa68edaf16f394aac324ae78fafa8e51bcd769b19707b2e5b3b202',
            'role': '対象預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '春日部支店', 
            'branch_code': '223', 
            'account_type': '普通預金', 
            'account': '3075321', 
            'name': 'プレセンタシオン アリス ヴイクトリア', 
            'amount': '151797', 
            'notice_date': '2025-04-16',
            'delete_date': '2025-06-16',
            'name_alias': 'PRESENTACION ALICE VICTORIA',
            "form": "k_pubstype_05_detail.php",
            "no": "2502-0001-0034",
            "pn": "371209",
            "p_id": "07",
            "re": "0",
            "referer": '0'
        }
        assert core.normalize_accounts(accounts[0])[0] == expected

@pytest.fixture
def k_pubstype_07_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_07_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_07_detail_1(k_pubstype_07_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_07_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_07_detail.php",
            "no": "2502-0005-0027",
            "pn": "373593",
            "p_id": "08",
            "re": "0",
            "referer": '0'
        }
        accounts = core._pubstype_detail(subject)

        # 三菱ＵＦＪ銀行ケースの確認
        expected = {
            'uid': '8a42e21bbb797231d2834f896a3fff6712c584817887bf73dbf6bd831e9e23f0',
            'role': '対象預金口座等に係る', 
            'bank_name': '三菱ＵＦＪ銀行', 
            'branch_name': '町田支店', 
            'branch_code': '228', 
            'account_type': '普通預金', 
            'account': '2549964', 
            'name': 'グエン ダン ビン', 
            'amount': '22004', 
            'effective_from': '2025年7月17日 0時', 
            'effective_to': '2025年10月15日 15時', 
            'effective_method': '被害回復分配金支払申請書を店頭に提出又は郵送（詳細は照会先へご連絡下さい）', 
            'payment_period': '2024年5月頃', 
            'suspend_date': '2025-07-01', 
            'reason': 'オレオレ詐欺',
            'notes': '', 
            "form": "k_pubstype_07_detail.php",
            "no": "2502-0005-0027",
            "pn": "373593",
            "p_id": "08",
            "re": "0",
            "referer": '0'
        }
        assert core.normalize_accounts(accounts[0])[0] == expected

        # 資金の移転元となった預金口座等に係る
        expected = {
            'uid': '54b7a9148d153aaaf3186d63338b0f6a80f4b41718043dc52e4145b65ced4edb',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '柏支店', 
            'branch_code': '329', 
            'account_type': '普通預金', 
            'account': '4157068', 
            'name': 'EBARDALOZA VEREGILIO', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '2024年5月頃', 
            'suspend_date': '', 
            'reason': 'オレオレ詐欺',
            'notes': '', 
            "form": "k_pubstype_07_detail.php",
            "no": "2502-0005-0027",
            "pn": "373593",
            "p_id": "08",
            "re": "0",
            "referer": '0'
        }
        assert core.normalize_accounts(accounts[1])[0] == expected

@pytest.fixture
def k_pubstype_09_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_09_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_09_detail_1(k_pubstype_09_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_09_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_09_detail.php",
            "no": "2411-0038-0042",
            "pn": "370345",
            "p_id": "12",
            "re": "0",
            "referer": '0'
        }
        accounts = core._pubstype_detail(subject)

        # 住信ＳＢＩネット銀行ケースの確認
        expected = {
            'uid': '13ec00f2fe66bbbdbe4ade01feed5ecef54877a0488057d31578fec13eabf867',
            'role': '対象預金口座等に係る', 
            'bank_name': '住信ＳＢＩネット銀行', 
            'branch_name': '法人第一支店', 
            'branch_code': '106', 
            'account_type': '普通預金', 
            'account': '2088276', 
            'name': 'ド） エース', 
            'amount': '237019', 
            'notes': '', 
            "form": "k_pubstype_09_detail.php",
            "no": "2411-0038-0042",
            "pn": "370345",
            "p_id": "12",
            "re": "0",
            "referer": '0'
        }
        assert core.normalize_accounts(accounts[0])[0] == expected

@pytest.fixture
def k_pubstype_10_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_10_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_10_detail_1(k_pubstype_10_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_10_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_10_detail.php",
            "no": "2415-9900-0114",
            "pn": "371720",
            "p_id": "11",
            "re": "0",
            "referer": '0'
        }
        accounts = core._pubstype_detail(subject)

        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': 'b7095c44bfb9f0e0dadcf7d6bce8236472e2448ec4f81bddc4685d46495b3779',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'name': 'チャン ヴァン カイン', 
            'amount': '20153', 
            'notice_date': '2025-01-16',
            'branch_code_jpb': '10330',
            'account_jpb': '89857121',
            'name_alias': 'TRAN VAN CANH',
            "form": "k_pubstype_10_detail.php",
            "no": "2415-9900-0114",
            "pn": "371720",
            "p_id": "11",
            "re": "0",
            "referer": '0'
        }
        assert core.normalize_accounts(accounts[0])[0] == expected

@pytest.fixture
def k_pubstype_10_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_10_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_10_detail_2(k_pubstype_10_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_10_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_10_detail.php",
            "no": "2412-0001-0028",
            "pn": "369725",
            "p_id": "11",
            "re": "0",
            "referer": '0'
        }
        accounts = core._pubstype_detail(subject)

        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': 'f60b488a2f135cb1f199923fb1f9e2df793049edd07f6b2522ba8c6db46d888d',
            'role': '対象預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '赤羽支店', 
            'branch_code': '203', 
            'account_type': '普通預金', 
            'account': '3118190', 
            'name': 'グエン テイ ホアイ ニエン', 
            'amount': '450709', 
            'notice_date': '2024-12-02',
            'name_alias': 'NGUYEN THI HOAI NHIEN',
            "form": "k_pubstype_10_detail.php",
            "no": "2412-0001-0028",
            "pn": "369725",
            "p_id": "11",
            "re": "0",
            "referer": '0'
        }
        assert core.normalize_accounts(accounts[0])[0] == expected