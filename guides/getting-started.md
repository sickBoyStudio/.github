# 🌱 로블록스 게임, 처음 만들어 보기

> 로블록스 게임을 한 번도 안 만들어 봤어도 괜찮습니다.
> 막히면 언제든 [소통창구 Q&A](https://github.com/sickBoyStudio/.github/discussions)에 물어보세요. 바보 같은 질문은 없습니다.

## 4주 로드맵

| 주차 | 목표 | 끝나면 할 수 있는 것 |
|---|---|---|
| 1주 | Studio 익히기 + 첫 스크립트 | 밟으면 죽는 발판, 문 열기 |
| 2주 | 서버/클라이언트, UI | 버튼 누르면 서버에 요청 보내기 |
| 3주 | 데이터 저장 + 첫 공개 | 코인이 저장되는 미니게임을 친구에게 공유 |
| 4주 | 수익화 + 협업 | 게임 패스 판매, 조직 레포에 첫 PR |

---

## 1. 준비물

- **Roblox 계정** — 꼭 **2단계 인증**을 켜세요. 게임과 수익이 걸린 계정입니다.
- **Roblox Studio** — [create.roblox.com](https://create.roblox.com)에서 받습니다. Windows와 macOS 모두 됩니다.
- **GitHub 계정** — 조직에 들어오거나 공동제작에 참여할 때 필요합니다. 여기도 2단계 인증.
- (나중에) **VS Code + Rojo + Git** — 여럿이 코드를 나눠 쓸 때 씁니다. 처음엔 Studio만으로 충분합니다.

## 2. 첫 게임 — 30분

1. Studio를 열고 **Baseplate** 템플릿으로 새로 만듭니다.
2. 왼쪽 **Explorer**에서 `ServerScriptService` 위에 마우스를 올리고 **+ → Script**를 추가합니다.
3. 아래 코드를 붙여 넣습니다. 밟으면 쓰러지는 빨간 발판입니다.

```lua
local part = Instance.new("Part")
part.Size = Vector3.new(6, 1, 6)
part.Position = Vector3.new(0, 1, -10)
part.BrickColor = BrickColor.new("Really red")
part.Anchored = true
part.Parent = workspace

part.Touched:Connect(function(hit)
	local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
	if humanoid then
		humanoid.Health = 0
	end
end)
```

4. **F5**(Play)로 실행해서 밟아 봅니다.
5. 안 되면 **View → Output** 창을 켜고 빨간 에러를 확인합니다. 질문할 때 이 에러를 그대로 붙여 주세요.

## 3. 꼭 알아야 하는 개념

| 개념 | 한 줄 설명 |
|---|---|
| **Script / LocalScript** | Script는 서버에서, LocalScript는 각 플레이어 컴퓨터(클라이언트)에서 실행됩니다. |
| **RemoteEvent** | 클라이언트 ↔ 서버가 신호를 주고받는 통로입니다. |
| **클라이언트를 믿지 말 것** | 해커는 클라이언트를 마음대로 조작합니다. 돈, 체력, 아이템 지급은 **항상 서버에서** 판단하세요. |
| **DataStore** | 플레이어 데이터를 저장합니다. Studio에서 테스트하려면 Game Settings → Security → *Enable Studio Access to API Services*를 켜야 합니다. |
| **Workspace / ReplicatedStorage / ServerStorage** | 보이는 세계 / 양쪽이 같이 쓰는 것 / 서버만 아는 것 |

## 4. 공개하기

1. **File → Publish to Roblox**로 올립니다. 처음엔 비공개 상태입니다.
2. [Creator Hub](https://create.roblox.com/dashboard/creations)에서 게임을 열고 아이콘, 썸네일, 설명을 채웁니다.
3. **성숙도·준수 설문(Maturity & Compliance Questionnaire)** 을 작성합니다. 작성하지 않으면 일반 유저에게 공개되지 않습니다.
4. 공개(Public)로 바꾸고, **공유 링크**로 친구를 초대하세요. 공유 링크로 들어온 신규 유저는 [Creator Rewards](roblox-revenue.md#3-creator-rewards--판매-없이-받는-보상) 대상이 될 수 있습니다.

> 💡 같이 만들 게임이라면 처음부터 **Roblox 그룹**을 만들어 그룹 이름으로 퍼블리시하세요. 나중에 수익을 자동으로 나눌 수 있습니다. ([법적 구조 8장](../policies/legal-structure.md#8-roblox-쪽-구조--게임은-그룹이-소유))

## 5. 첫 수익 — 게임 패스

1. Creator Hub → 게임 → **Monetization → Passes**에서 패스를 만들고 가격을 정합니다.
2. 게임 안에서 판매창을 띄우고, 산 사람에게 혜택을 줍니다.

```lua
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local PASS_ID = 0 -- 만든 패스의 ID로 바꾸세요

Players.PlayerAdded:Connect(function(player)
	local ok, owns = pcall(MarketplaceService.UserOwnsGamePassAsync, MarketplaceService, player.UserId, PASS_ID)
	if ok and owns then
		player:SetAttribute("VIP", true)
	end
end)
```

판매가의 70%가 개발자 몫이고, 30,000 Robux가 모이면 현금으로 바꿀 수 있습니다. 자세한 숫자는 [로블록스 수익구조](roblox-revenue.md)를 보세요.

## 6. 안전 수칙 — 이것만은 꼭

- 🦠 **무료 모델 조심**: 툴박스 모델에 숨은 Script가 게임을 망가뜨리거나 관리자 권한을 빼앗습니다. 넣은 뒤 `require(`, `getfenv`, `loadstring`을 검색해 보세요.
- 🍪 **`.ROBLOSECURITY` 쿠키를 절대 남에게 주지 마세요.** 비밀번호보다 위험합니다. "이거 붙여 넣으면 Robux 줌" 같은 건 100% 계정 탈취입니다.
- 🎵 **음악은 라이선스가 확인된 것만.** 유명 노래를 올리면 삭제되고 계정이 제재될 수 있습니다.
- 💱 **Robux를 현금으로 사고팔지 마세요.** 이용약관 위반입니다.
- 🔌 **출처를 모르는 플러그인은 설치하지 마세요.**

## 7. 함께 만들기 — 우리 조직 방식

로블록스 안의 **Team Create**로도 같이 만들 수 있지만, 누가 무엇을 만들었는지 기록이 남지 않습니다.
sickBoyStudio는 **GitHub 레포 + Rojo**로 코드를 관리하고, **PR 기록을 수익 분배의 근거**로 씁니다.

1. 마음에 드는 레포에 **🤝 공동제작 참여 신청** 이슈를 엽니다.
2. 오너가 받아 주면 작업하고 PR을 보냅니다.
3. PR이 merge되면 `CONTRIBUTORS.yml`에 자기를 추가하는 PR을 보냅니다 → **수익 5%**.

자세한 절차: [공동제작 참여 가이드](../CONTRIBUTING.md)

## 8. 공부 자료

- [Creator Hub 한국어 문서](https://create.roblox.com/docs/ko-kr) — 공식 튜토리얼과 API 레퍼런스
- [Luau](https://luau.org) — 로블록스 스크립트 언어 공식 사이트
- [Rojo](https://rojo.space) — Studio 밖(VS Code)에서 코드를 쓰고 Git으로 관리하는 도구
- [Roblox DevForum](https://devforum.roblox.com) — 전 세계 개발자 커뮤니티 (영어)

## 9. 질문 잘하는 법

소통창구 **🙋 Q&A**에 아래를 담아 주세요. 양식이 알아서 물어봅니다.

1. **하고 싶은 것**: "문을 E키로 열고 싶어요"
2. **해 본 것**: 코드 (```` ```lua ```` 블록으로 감싸기)
3. **결과**: Output 창의 에러 메시지 그대로, 스크린샷
4. **환경**: Studio인지 실제 서버인지, 혼자인지 여러 명인지
