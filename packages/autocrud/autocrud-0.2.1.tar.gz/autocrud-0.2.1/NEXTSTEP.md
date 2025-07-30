- ✅ MultiModelAutoCRUD才是主要使用的class，需要被改名成AutoCRUD，原本的AutoCRUD改成其他名字
- ✅ MultiModelAutoCRUD的storage為什麼只有一個? storage應該跟resource深度綁定
- ✅ create_routes應該可以直接吐一個fastapi router出來，不需要吃app進去
- ✅ 我們應該要讓user自己建立type的id、created_time、created_by、updated_time、updated_by，再用調用的方式去access object，而不是自動地在type上面硬寫id field，不然user create出來的type無法在project內部復用 (缺id等等attribute)。i.e., user需要創建最完整的schema，包含id, created_time, ...。我們必須根據這個schema自動推倒出
    1.create的body需要長甚麼樣(e.g., 不需要有id, times，不需要udated_by，created_by可選是從function取得或是必須在body中(function取得可能是透過request cookie)
    2. update的body (前面敘述過)，也不需要有id、created_time、created_by、updated_time、updated_by，但是一樣update_by要讓user可選是從哪來。
- ✅ get應該回傳list of resource，而不是dict
- ✅ 新增created_time、created_by、updated_time、updated_by，這些項目是optional，可以選擇是否開啟，以及開啟之後的attribute name是甚麼
- ✅ key name可選，預設用id沒問題，但可以讓user選擇其他名稱，例如pk、_id等等
- ✅ update使用特殊的updater，對每個attribute做細部adjust，而不是每次都要傳完整的body
    - ✅ undefined: 不改變
    - ✅ 有值: 改成該值
    - ✅ list attribute: 提供"改整個list"，"新增items by list[value]"，"刪除items by list[value]"
    - ✅ dict attribute: 提供"改整個dict"，"新增items by dict[key, value]"，"刪除items by list[key]"
- ✅ 我應該能夠直接使用AutoCRUD (和MultiModelAutoCRUD)新增route
- ✅ 每個route應該都要可選，而不是一股腦全部給出去
- ✅ 列出所有資源應該要能吃params來support
  1. ✅ pagination
  2. ✅ filter by created_by/updated_by (list)
  3. ✅ filter by created_time/updated_time (range)
  4. ✅ sort by created_time/updated_time (incr/decr)
- ✅ typing，希望可以可以使用typing方法，例如AutoCRUD[XXX]來指定這個crud的resource type
- ✅ metadata config只能在SingleModelCRUD給，但在AutoCRUD給才是最常用的選項，包含id_generator，也許是在init時給，也可以在register model時給 (update init給的)，如果某些attriute沒給，還是fallback到init給的那些
- ✅ use_plural應該也能在autocrud init時給
- ✅ _is_optional_field如果是typeddict的話，如果有在register_model時給default value，就可以把它視為optional，不然對typeddict user太不友善
- ✅ 允許api background task，也許放在RouteConfig裡面，也許RouteConfig的attribute type不應該是bool，讓我們能更細緻的調整每個route的行為
- ✅ 實作custom_dependencies的功能
- ✅ resource name自動生成可以選擇snake、camel、dash
- ✅ 支援get model by model class而不是只能access by resource name，也要注意一個model註冊兩次(resource name不同)的話，用這樣的方式access時要跳錯
- ✅ 讓我們統一backgroun task的callback signature，只收一個input，就是該router的output (不是response object，完全就是那個router function的output)，所以我們甚至可以使用一些手法讓所有router (get/update/create/delete/...)都套用同一個bgtask邏輯
- ✅ 可以支援plugin其他種類的route，我們需要定義plugin的interface，user可以實作並透過我們的方法注入到我們的系統中，接著在autogen routes時，也跑他的東西。
  1. 第一先讓我們自己的route都符合該設計好的interface
  2. 我們自己的route都以default注入的形式進入我們的系統
  3. 讓user也能注入他們的route
