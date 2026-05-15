import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

#配置页面的配置项
st.set_page_config(
    page_title="智能助手-黑丝女仆",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",

)

#加载所有会话列表
def load_sessions():
    session_list = []
    #加载sessions目录下的文件名
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[0:-5])
    session_list.sort(reverse=True) #排序，降序
    return session_list

#加载指定的会话信息
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            #读取会话信息
            with open(f"sessions/{session_name}.json","r",encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception as e:
        st.error(f"加载会话失败:{e}")

#删除指定会话信息
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")  #删除文件
            if session_name == st.session_state.current_session: #如果删除是的当前会话，则需要跟新消息列表
                st.session_state.messages = []
                st.session_state.current_session = get_session_name()
    except Exception as e:
        st.error(f"删除会话失败：{e}")


#生成会话标识函数
def get_session_name():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#保存会话信息函数
def save_session():
        # 保存当前会话
        if st.session_state.current_session:
            # 构建新的会话
            session_date = {
                "nick_name": st.session_state.nick_name,
                "nature": st.session_state.nature,
                "current_session": st.session_state.current_session,
                "messages": st.session_state.messages
            }
            # 如果sessions 文件存在，则创建
            if not os.path.exists("sessions"):
                os.mkdir("sessions")

            # 保存会话
            with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
                json.dump(session_date, f, ensure_ascii=False, indent=2)

#大标题
st.title("智能助手-黑丝女仆")

#系统提示词
# %s 动态显示
system_prompt = """
        你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。：
        规则：
            1、每次只回1条消息
            2、禁止任何场景或状态描述性文字
            3、匹配用语言
            4、回复简短，像微信聊天一样
            5、有需要的话，可以用🌹等emoji表情
            6、用符合伴侣性格的方式对话
            7、回复的内容，要充分体现伴侣的性格特征
        伴侣性格：
            %s
        你必须严格遵守上述规则来回复用户
            """

#初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "黑丝女仆"

#性格
if "nature" not in st.session_state:
    st.session_state.nature = "活泼、开放、幽默的台湾腔姑娘"

#会话的名字
if "current_session" not in st.session_state:
    st.session_state.current_session = get_session_name()  #系统时间作为文件名字

# 左侧侧边栏
with st.sidebar:
    st.subheader("黑丝女仆信息")

    # 新建会话
    if st.button("新建会话", width="stretch", icon="🖊️"):
        #保存当前会话
        save_session()

        #创建新的会话
        if st.session_state.messages:  #如果两天记录非空，则为True，否则为False
            st.session_state.messages = []
            st.session_state.current_session = get_session_name()
            save_session()
            st.rerun () #重新运行程序

    #会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        with col1:
            #点击这个按钮，就会加载会话信息：
            #三元运算符：如果条件为真，则返回第一个表达式的值；否则返回第二个表达式的值--->语法：值1 if 条件 else 值2
            if st.button(session,icon="📖",width="stretch",key=f"load_{session}",type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            #删除指定会话
            if st.button("",icon="❌",width="stretch",key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

#分割线
    st.divider()   # 在项目目录下


    #昵称输入框
    nick_name = st.text_input("请输入昵称：",placeholder="帮我起个名",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    #性格输入框
    nature = st.text_input("请输入性格：",placeholder="你想要乜类型噶女仔",value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

#展示聊天信息
st.text(f"会话名称:{st.session_state.current_session}")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


#消息输入框
prompt = st.chat_input("你up乜春啊？")
if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    print("调用AI大模型，提示词：", prompt)
    #保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    #调用AI大模型
    # 配置 API Key 和 Base URL
    API_KEY = "ak_2G00oi8mM9To7kD5Js1hY1ca4fk8F"
    BASE_URL = "https://api.longcat.chat/openai/v1"

    # 初始化客户端
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    response = client.chat.completions.create(
        model="LongCat-Flash-Chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages   # 星号 *，解包作用
        ],
        stream=True
    )

#流式输出：
    full_response = ""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    #保存大模型返回的内容
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    #保存会话信息
    save_session()
