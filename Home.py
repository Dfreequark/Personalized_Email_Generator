import streamlit as st
import pandas as pd
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import smtplib
import os
import utils

st.set_page_config(page_title="Personalized Email Generator", page_icon="📧")

st.title("Personalized Email Generator📧")


os.environ["COHERE_API_KEY"] = utils.user_api_key()

class EmailGenerator:
    def __init__(self, user_want, user_field, user_information):
        # Initialize API and other configurations
        self.llm = utils.configure_llm()
        self.init_session_state()
        self.user_want = user_want
        self.user_field = user_field
        self.user_information = user_information
        self.df = None
        self.llm_chain = self.init_llm_chain()
        

    def init_session_state(self):
        # Initialize session states for chat and file processing
        if "csv_data" not in st.session_state:
            st.session_state.csv_data = pd.DataFrame([])
        if "send_email_flag" not in st.session_state:
            st.session_state.send_email_flag = False
        


    def init_llm_chain(self):
        # Define LLM prompt template
        prompt_template = """
        You are an excellent assistant and you write quality and professional emails. Write a persuasive cold email to {Name}, who works at {Company} on {Description}."""
        prompt_template += """
        The aim is to ask for {want} in this field/role: {field}
        My information: {information}
        STRICTLY FOLLOW the sample format, under 50 words:
        <greeting> \n\n
        <paragraph 1: short and precise one line introduction of mine> \n\n
        <paragraph 2: appreciate their work in one sentence>\n\n
        <paragraph 3: ask what i want directly and offer them to help>\n\n 
        Sincerely, 
        <my name>
        """.format(want =self.user_want, field =self.user_field, information = self.user_information)
    
        prompt = PromptTemplate(template=prompt_template, input_variables=["Name", "Company", "Description"])
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        return llm_chain

    def send_email(self, subject, body, recipient_email):
        sender_email = ""  # Replace with your email
        sender_password = ""  # Replace with your email app password

        message = f"Subject: {subject}\n\n{body}"

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.encode('utf-8'))

            
            st.write((f"Email successfully sent to {recipient_email}"))
        
        except Exception as e:
            st.error(f"Failed to send email to {recipient_email}: {e}")

# Function to send emails from the CSV file
    def send_from_csv(self, df):
        for _, row in df.iterrows():
            company = row['Company']
            email = row['Email']
            body = row['Message']
            subject = f"Passionate About {self.user_field}: {self.user_want} Inquiry for {company}"
            self.send_email(subject, body, email)

    def process_csv_file(self):
        # File upload widget
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file :
            self.df = pd.read_csv(uploaded_file)
            st.session_state.send_email_flag = False  # Reset email sending flag

            if 'Name' in self.df.columns and 'Company' in self.df.columns and 'Email' in self.df.columns:
                st.write("CSV file successfully loaded.")
                st.write(self.df)
                return True
            else:
                st.error("The CSV file must contain 'Name', 'Company', 'Email' and 'Description' columns.")
        return False
    

    def generate_messages(self):
        # Chat message widget to process the conversation with AI
        with st.sidebar:
            st.write("PRESS THIS BUTTON TO GENERATE NEW MAILS!⚠️")
            generate_btn = st.button("Generate personalized emails!")

        if generate_btn:
            for _, row in self.df.iterrows():
                name = row['Name']
                company = row['Company']
                description = row['Description']
                personalized_message = self.llm_chain.run({"Name": name, "Company": company, "Description":description })
                self.df.loc[self.df['Name'] == name, 'Message'] = personalized_message

            
            st.session_state.chat_history.append("Emails generated successfully!")
            st.session_state.csv_data = self.df 

    def download_and_send(self):

        # Handle the option to download and send emails
        df = st.session_state.csv_data
        
        # if df.at[0, "Message"]:
        if "Message" in st.session_state.csv_data:
            with st.chat_message("assistant"):
                st.write("Generated messages:")
                st.write('dataframe', df)

            # Option to download CSV with messages
            csv = df.to_csv(index=False).encode('utf-8')

            st.download_button(label="Download CSV with Messages", data=csv, file_name='personalized_messages.csv', mime='text/csv')

            
            # Ask if the user wants to send emails
            
            
            st.write("Do you want to send email?")
            yes_btn = st.button("YES")
            no_btn = st.button("NO")

            # Step 4: Handle email sending
            if yes_btn:
                st.session_state.send_email_flag = True
                st.write("This feature is disabled due to security reason") # comment this while sending mails
            elif no_btn:
                st.session_state.send_email_flag = False
          
            if st.session_state.send_email_flag:
                # self.send_from_csv(df)     # uncomment this to send mails
                st.session_state.send_email_flag = False  # Reset email sending flag after completion

    def manage_chat_history(self):
        # Display chat history
        for message in st.session_state.chat_history:
            st.chat_message("assistant").write(message)
    
    def main(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Step 1: Process CSV file
        if self.process_csv_file():
            # Step 2: Generate messages
            self.generate_messages()

            # Step 3: Manage chat history
            self.manage_chat_history()

            # Step 4: Download and send emails
            self.download_and_send()
if __name__ =="__main__":
    # Main method to run the application
    
    # information input
    st.write("Please fillup the following fields to generate output mails")
    user_want = st.selectbox(
    "What is the purpose of your mail?",
    ("Internship", "Mentorship", "Advice", "Other"), 
)
    if user_want =="Other":
        user_want= st.text_input("Type the purpose of your mail here:")
    
    user_field = st.text_input("Enter the sector/field/role you are in(eg. generative ai/ business development etc)")
    user_information =st.text_input("Write about yourself to enhance output(eg name, your passion etc)")

    if "user_want" not in st.session_state:
            st.session_state.user_want = ""
    if "user_field" not in st.session_state:
        st.session_state.user_field = ""
    if "user_information" not in st.session_state:
        st.session_state.user_information = ""
    
    
    st.session_state.user_want, st.session_state.user_field, st.session_state.user_information = user_want, user_field, user_information

    if st.session_state.user_want and st.session_state.user_field and st.session_state.user_information:
        st.write("Upload a CSV file with 'Name', 'Company', 'Email' and 'Description' columns to generate personalized emails.")
        # Instantiate and run the app
        assistant = EmailGenerator(user_want, user_field,user_information)
        assistant.main()
        
        
        



