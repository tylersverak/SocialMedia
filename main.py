"""
TYLER SVERAK
A program to automate sending of an email newsletter.

While the email contents should be generated elsewhere, the content is congregated and
sent here. All images from the 'Images' subfolder will be send as attachments. There is no
programmatic limit to the number of images sent but there are likely practical limitations.
"""
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart 
import smtplib 
import imaplib
import os
from secret import secrets
from PIL import Image
from datetime import datetime
from O365 import Account


# Given the path to a JFIF image, replaces it with a JPEG version
# @Upgrade: Consider expanding to work for all file types
def convert_jfif_to_jpg(jfif_filename):
    with Image.open(jfif_filename) as img:
        rgb_img = img.convert('RGB')  # Convert to RGB to ensure compatibility
        jpg_path = jfif_filename[:-4] + "jpeg"
        rgb_img.save(jpg_path, 'JPEG')


# Loops through the images in the 'Images' subfolder and converts them to JPG,
# if necessary.
# Returns a list of strings, containing <img> tags pointing to the given images
def get_images(msg):
    image_dir = 'images'
    image_tags = []

    # loop through images to be attached
    for filename in os.listdir(image_dir):

        # remove spaces from file names
        if " " in filename:
            spaceless_filename = filename.replace(" ", "_")
            with Image.open(image_dir + "/" + filename) as img:
                img.save(image_dir + "/" + spaceless_filename)
            os.remove(image_dir + "/" + filename)
            filename = spaceless_filename

        # convert jfif
        if filename.lower().endswith("jfif"):
            convert_jfif_to_jpg(filename)
        # technically if you had a jfif with the same name as an existing jpeg image it would replace it but that's niche

        # handle other image types
        if filename.lower().endswith(('png', 'jpg', 'jpeg')):
            # Path to the image file
            image_path = os.path.join(image_dir, filename)
            
            # Open and read the image file
            with open(image_path, 'rb') as img_file:
                # Create a MIMEImage object
                img = MIMEImage(img_file.read())
                img.add_header('Content-ID', f'<{filename}>')
                img.add_header('Content-Disposition', 'inline', filename=filename)
                
                # Attach the image to the email
                msg.attach(img)
            
            # Create an HTML <img> tag for the image
            image_tags.append(f'<img src="cid:{filename}" alt="{filename}" style="max-width: 600px; margin-top: 20px;" />\n<br>')
        
    return image_tags


# Returns a string composed of HTML, to be put in the body of the email as text.
def make_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333333;
                margin: 20px;
            }}
            h1 {{
                color: #4CAF50;
            }}
            p {{
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
        <h1>Man I Love Fishing!{date}</h1>
        <p>This is a simple FISHING email.</p>
        <p>Not like phishing but like actually getting fish out of water.</p>
        {images}
    </body>
    </html>
    """


# Uses make_html and get_images to gather the email contents and combine them.
# Returns a MIMEMultipart object with the email contents.
def email_content():
    # creating email text
    msg = MIMEMultipart()
    msg['Subject'] = "html email"
    html_content = make_html()

    # attach images
    image_tags = get_images(msg)
    html_content = html_content.format(images='\n'.join(image_tags),date=datetime.now().strftime("%B %d, %Y"))
    msg.attach(MIMEText(html_content, 'html'))

    print("Email prepared...")
    return msg

def main():

    # create the actual email contents
    msg = email_content()

    # setup connection to smtp server
    connection_open = True
    try:
        # verify credentials work
        print("Establishing connection...")
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(secrets.MYADDRESS, secrets.APPPASSWORD)

        # send the email to everyone on the mailing list
        msg_str = msg.as_string()
        for target_addr in secrets.TARGETADDRESSES:
            smtp.sendmail(from_addr=secrets.MYADDRESS,to_addrs=target_addr, msg=msg_str)
        smtp.quit()
        connection_open = False
        print("All emails sent, connection closed, all done!")
    except Exception as e:
        print("Log in or sending failed:",e)
    finally:
        if connection_open:
            smtp.quit()

if __name__=="__main__":
    main()
