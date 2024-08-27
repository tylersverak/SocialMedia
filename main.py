
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage 
from email.mime.application import MIMEApplication 
from email.mime.multipart import MIMEMultipart 
import smtplib 
import os
from secret import gmailpasswords as secrets
from PIL import Image

def convert_jfif_to_jpg(jfif_path, jpg_path):
    with Image.open(jfif_path) as img:
        rgb_img = img.convert('RGB')  # Convert to RGB to ensure compatibility
        rgb_img.save(jpg_path, 'JPEG')

def get_images(msg):
    image_dir = 'images'
    image_tags = []

    # loop through images to be attached
    for filename in os.listdir(image_dir):

        # remove spaces from file names
        if any(char.isspace() for char in filename):
            spaceless_filename = filename.replace(" ", "_")
            with Image.open(image_dir + "/" + filename) as img:
                img.save(image_dir + "/" + spaceless_filename)
            os.remove(image_dir + "/" + filename)
            filename = spaceless_filename

        # convert jfif
        if filename.lower().endswith("jfif"):
            jpeg_filename = filename[:-4] + "jpeg"
            convert_jfif_to_jpg(image_dir + "/" + filename,image_dir + "/" + jpeg_filename)
        # technically if you had a jfif with the same name as an existing jpeg it would replace it but that's niche

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



def email_content():

    # creating email text
    msg = MIMEMultipart()
    msg['Subject'] = "html email"
    html_content = """
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
        <h1>Man I Love Fishing!</h1>
        <p>This is a simple FISHING email.</p>
        <p>Not like phishing but like actually getting fish out of water.</p>
        {images}
    </body>
    </html>
    """

    # attach images
    image_tags = get_images(msg)
    html_content = html_content.format(images='\n'.join(image_tags))
    msg.attach(MIMEText(html_content, 'html'))

    print("Email prepared...")
    return msg

def main():

    # create the actual email contents
    msg = email_content()

    # setup connection to smtp server
    connection_open = True
    try:
        print("Establishing connection...")
        smtp = smtplib.SMTP('smtp.office365.com', 587)
        smtp.ehlo() 
        smtp.starttls() 
        smtp.login(secrets.MYADDRESS, secrets.APPPASSWORD)

        # send the email to everyone on the mailing list
        msg_str = msg.as_string()
        for target_addr in secrets.TARGETADDRESSES:
            smtp.sendmail(from_addr=secrets.MYADDRESS,to_addrs=target_addr, msg=msg_str)
        smtp.quit()
        connection_open = False
        print("All emails sent, connection closed, all done!")
    finally:
        if connection_open:
            smtp.quit()

if __name__=="__main__":
    main()
