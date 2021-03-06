from django.shortcuts import render, HttpResponse
from .forms import SingleUserDetailForm, SheetForm
from .models import SheetModel
import os
import numpy as np, pandas as pd
import pickle
import lightgbm
from django.core.mail import send_mail
from django.conf import settings
import datetime as dt



"""
name: Single user report
desc: banks can put in the data of the users and get their score for loan prediction
"""
def SingleUserReport(request):
    form = SingleUserDetailForm()
    out = None
    if request.method == "POST":
        form = SingleUserDetailForm(request.POST)
        if form.is_valid():
            # getting the inputs
            email = form.cleaned_data['email']
            mail_send = form.cleaned_data['send_mail']
            ip = [int(form.cleaned_data['education']),int(form.cleaned_data['income']),int(form.cleaned_data['credit']),int(form.cleaned_data['property_area']),int(form.cleaned_data['amount_term']),int(form.cleaned_data['marital_status']),int(form.cleaned_data['loan_amount'])*100]

            # deserializing objects
            lgbm = lightgbm.Booster(model_file='dependencies/lgbm_base.txt')
            scaler = pickle.load(open('dependencies/scaler.pkl','rb'))

            # scaling
            ip = scaler.transform([ip])

            # prediction
            out = round(lgbm.predict(np.array(ip,dtype=np.int32))[0])

            if out:
                out = "Eligible for Loan"
            else:
                out = "Not Eligible for Loan"

            if mail_send:
                subject = "Loan Approval Status"
                message = f"""
                    Dear Cusomer,
                    Your Loan Status: {out}
                """
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                send_mail(subject,message,email_from,recipient_list)

    return render(request,'report/single_user.html',{'form':form, 'out':out})

"""
name: Sheet Report
description: csv file is uploaded and the view returns the csv along with predictions
"""
def SheetReport(request):
    form = SheetForm()
    if request.method == "POST":
        form = SheetForm(request.POST,request.FILES)
        if form.is_valid():

            mail_send = form.cleaned_data.pop('mail_send')

            sheet = SheetModel(**form.cleaned_data,bank=request.user)
            sheet.save()
            
            test_df = pd.read_csv(sheet.sheet.path)
            test_df.drop(['Unnamed: 0'],axis=1,inplace=True)
            test_df_array = test_df[['Education','ApplicantIncome','Credit_History','Property_Area','Loan_Amount_Term','Married','LoanAmount']].to_numpy()

            lgbm = lightgbm.Booster(model_file='dependencies/lgbm_base.txt')
            scaler = pickle.load(open('dependencies/scaler.pkl','rb'))

            test_df_array = scaler.transform(test_df_array)
            preds = lgbm.predict(test_df_array)
            test_df['Predictions'] = np.round(preds)

            eligible_df = test_df[test_df['Predictions'] == 1]
            not_eligible_df = test_df[test_df['Predictions'] == 0]

            if mail_send:
                subject = "Loan Approval Status"
                message = f"""
                    Dear Cusomer,
                    Your Loan Status: Eligible for Loan.
                """
                email_from = settings.EMAIL_HOST_USER
                recipient_list = list(eligible_df['Email'])
                send_mail(subject,message,email_from,recipient_list)

                message = f"""
                    Dear Cusomer,
                    Your Loan Status: Eligible for Loan.
                """
                recipient_list = list(not_eligible_df['Email'])
                send_mail(subject,message,email_from,recipient_list)

            os.remove(sheet.sheet.path)
            sheet.delete()

            response = HttpResponse(content_type='text/xlsx')
            response['Content-Disposition'] = 'attachment; filename=export.xlsx'
            with pd.ExcelWriter(response,engine='xlsxwriter') as writer:    
                eligible_df.to_excel(writer, sheet_name='Sheet1')
                not_eligible_df.to_excel(writer, sheet_name='Sheet2')
        

            
            return response

    return render(request,'report/sheet.html',{'form':form})