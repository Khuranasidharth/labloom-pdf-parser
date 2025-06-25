HOW TO DEPLOY:

1. Replace your existing backend repo with these files.
2. Push to GitHub (make sure it's connected to Render).
3. Render will auto-deploy.
4. Your live endpoint will be: https://your-app-name.onrender.com/parse-pdf
5. Test with Postman or your frontend!

NOTE:
- This uses pdfplumber to extract real text from PDFs.
- You can enhance this further by detecting reference ranges or table layouts.