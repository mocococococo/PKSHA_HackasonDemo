import requests

class ZipcodeValidator:
    """
    郵便番号の形式を検証するクラス
    """

    @staticmethod
    def validate(postal_code: str) -> bool:
        """
        郵便番号が存在するかを検証する
        """
        if not postal_code:
            print("郵便番号が空です。")
            return False
        if len(postal_code) != 7:
            print(f"郵便番号の長さが不正です: {postal_code} (7桁でなければなりません)")
            return False
        if not postal_code.isdigit():
            print(f"郵便番号に数字以外の文字が含まれています: {postal_code}")
            return False
            
        request = "https://zipcloud.ibsnet.co.jp/api/search?zipcode={}".format(postal_code)
        response = requests.get(request)
        # レスポンスをJSON形式に変換
        response = response.json()
        # JSONレスポンスから必要な情報を抽出
        message = response["message"]
        results = response["results"]
        status = response["status"]
        if status != 200:
            print(f"郵便番号 {postal_code} の検証に失敗しました: {message}")
            return False
        if not results:
            print(f"郵便番号 {postal_code} は存在しません。")
            return False
        
        print(f"APIリクエスト: {request}")
        print(f"APIレスポンス: {response}")
        
        return True
        
if __name__ == "__main__":
    # テスト用の郵便番号
    test_postal_code = "1000001"  # 東京の例
    is_valid = ZipcodeValidator.validate(test_postal_code)
    print(f"郵便番号 {test_postal_code} の検証結果: {is_valid}")