# To-Eat-List 数据设计

## 1. 用户表 user
用于记录长期偏好与基础设置。

字段建议：

- id
- name
- gender
- height
- weight
- health_goal
- taste_preference
- dislike_food
- spicy_level
- milk_tea_limit_per_week
- email

## 2. 外卖表 food_item
用于记录学校周边外卖信息。

字段建议：

- id
- store_name
- food_name
- price
- category
- taste_tag
- nutrition_tag
- calorie_level
- is_milk_tea
- is_new_found
- remark

说明：
- `category`：米饭 / 面食 / 轻食 / 炸物 / 奶茶 / 水果等
- `taste_tag`：辣 / 甜 / 咸 / 清淡 / 重口等
- `nutrition_tag`：高蛋白 / 高糖 / 高脂 / 均衡 / 清淡等

## 3. 每日记录表 daily_record
用于记录当天输入和推荐结果。

字段建议：

- id
- date
- budget
- today_taste
- wanted_food
- already_had_milk_tea
- mood
- recommended_food
- alternative_food
- final_choice
- total_cost
- nutrition_comment
- milk_tea_comment

## 4. 奶茶记录表 milk_tea_record
用于记录奶茶摄入情况。

字段建议：

- id
- date
- drink_name
- brand
- sugar_level
- size
- price
- note

## 5. 邮件记录表 email_log
用于记录是否成功发送总结邮件。

字段建议：

- id
- date
- receiver_email
- subject
- content_summary
- send_status
- send_time