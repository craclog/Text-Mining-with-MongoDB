# Text-Mining-with-MongoDB
Using Apriori algorithm, News data Morphological analysis


## 기능
1. Morph
> 모든 뉴스 기사에 대해 제공된 형태소 분석 소스 코드와 불용어 리스트 파일을 이용해 텍스트 분석에 불필요한 단어(불용어)를 제거하고, 형태소 열이 추가된 상태로 데이터베이스를 update한다.
> 모든 뉴스 기사에 대해 각 기사에 나오는 단어들을 확인하고, 그 단어들을 집합으로 만들어 새로운 collection에 저장한다.

2. Print morphs
> 사용자로부터 뉴스 기사의 url을 입력 받아 해당하는 뉴스 기사의 형태소들을 출력해준다.

3. Print wordset
> 사용자로부터 뉴스 기사의 url을 입력 받아 해당하는 뉴스 기사의 Wordset을 출력해준다.

4. Frequent item set
> frequent 1-itemset, frequent 2-itemset, frequent 3-itemset을 형성하고 DB에 저장한다.

5. Association rule
> frequent n-th item set의 n을 입력 받았을 때, frequent n-th itemset에서의 strong 연관 규칙을 모두 출력한다. (min_conf = 50%)
