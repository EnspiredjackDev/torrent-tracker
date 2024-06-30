# Simple torrent tracker  
This is just a simple little script / website combo for tracking torrents  
This requires no external services (other than opentracker)  
  
The backend uses opentracker with a whitelist to ensure that only trackers that are uploaded to the website are tracked  

## Installation (for Production)

Follow these steps to set up the project:

1. **Clone the Repository**
   ```sh
   git clone https://github.com/EnspiredjackDev/torrent-tracker
   ```

2. **Build OpenTracker**
   - Follow the build instructions for [OpenTracker](https://erdgeist.org/arts/software/opentracker).
   - Ensure `FEATURES+=-DWANT_ACCESSLIST_WHITE` is uncommented in the Makefile.

3. **Build the Frontend**
   - Open a terminal in the `torrent-tracker-ui` folder and run:
     ```sh
     npm install && ng build torrent-tracker-ui -c production
     ```

4. **Prepare the Directory Structure**
   - Navigate to the `./dist/torrent-tracker-ui/browser/` directory within the `torrent-tracker-ui` folder.
   - Create a `static` folder in the location where you will run the website.
   - Copy all the files from the `./dist/torrent-tracker-ui/browser/` directory into the `static` folder.

5. **Organise Files**
   - Ensure `opentracker` and `using_opentracker.py` are in the same directory where the `static` folder resides.

   Your directory structure should look like this:
   ```
   project_root/
   ├── opentracker
   ├── using_opentracker.py
   ├── static/
   │   ├── index.html
   │   ├── main.js
   │   ├── styles.css
   │   └── ... (other compiled frontend files)
   ```

6. **Install Python Dependencies**
   ```sh
   pip install flask flask_sqlalchemy sqlalchemy gunicorn
   ```

7. **Run the Application**
   ```sh
   gunicorn -w 2 -b 0.0.0.0:5000 using_opentracker:app
   ```

   (above made with ChatGPT)  
## Features
- Tracks torrents "itself"
- Only allows torrents listed on the website to be tracked
- Uses magnet links only, no dealing with files
- Has PoW Captcha with adjustable difficulty in backend
- Uses SQL lite database
- Has admin controls

## Things you should know
- acceptable_categories on line 22 of backend is where the catagories the backend will accept are set, however categories on line 14 of add-torrent.componenent.ts and line 16 of torrents-list.component.ts will also need to reflect this change, otherwise it will be confusing
- ADMIN_KEY line 24 of backend should change otherwise someone can have full control of the site
- The database and whitelist *should* automatically generate on first run
- I have no clue how good this would be with a lot of users, I've not tested it with more than just myself
