from flask import Flask, render_template, request, redirect, session,jsonify,url_for
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('127.0.0.1', 27017)
db = client['jabi'] # database name
c = db['paper'] # collection name
c_new = db['sami']
app = Flask(__name__)
app.secret_key = "afsa"

# home handler-register page
@app.route('/')
def homePage():
    return render_template('ex1.html')

# home handler-register page
@app.route('/home')
def main():
    return render_template('index.html')

#viewdb is here
@app.route('/alldbs')
def  getAllDBS():
    return render_template('viewdb.html')




#new sucess code here
@app.route('/create_database', methods=['POST'])
def create_database():
    db_name = request.form.get('db_name')

    if not db_name:
        return jsonify(err='Please enter a valid database name.')

    existing_databases = client.list_database_names()
    if db_name in existing_databases:
        return jsonify(err='Database with the same name already exists.')

    new_db = client[db_name]
    return jsonify(success=f'Database "{db_name}" created successfully.')

@app.route('/create_collection', methods=['POST'])
def create_collection():
    db_name = request.form.get('db_name')
    collection_name = request.form.get('collection_name')

    if not db_name:
        return jsonify(err='Please enter a valid database name.')

    if not collection_name:
        return jsonify(err='Please enter a valid collection name.')

    db = client[db_name]
    db.create_collection(collection_name)
    return jsonify(success=f'Collection "{collection_name}" created in database "{db_name}".')



# login handler-login page
@app.route('/login')
def loginPage():
    return render_template('login.html')

# login handler-login page
@app.route('/create')
def createPage():
    return render_template('db.html')

@app.route('/dash')
def dashboardPage():
    # Retrieve the user's name from the session
    owner = session.get('username')

    # Check if the user is logged in (i.e., their name is stored in the session)
    if owner is None:
        return render_template('login.html', err1='Please log in first.')

    return render_template('dashboard.html', owner=owner)

# template handler
@app.route('/temp')
def templatesPage():
    return render_template('template.html')

@app.route('/map')
def mapyear():
    return render_template('indexs.html')
@app.route('/allinone')
def allinone():
    return render_template('allpages.html')

@app.route('/loggingout')
def Pagelogout():
    return render_template('login.html')


# template handler
@app.route('/pap1')
def PaperPage():
    return render_template('qp.html')

# template handler
@app.route('/pap2')
def PaperPagee():
    return render_template('qpp.html')

@app.route('/twoinone')
def twoin():
    return render_template('twoinone.html')

# template handler
@app.route('/pap3')
def PaperPages():
    return render_template('Qp.html')

#data collection handler
@app.route('/collection')
def  collectData():
    return render_template('data.html')

@app.route('/viewcol')
def  viewcat():
    return render_template('viewdata.html')

@app.route('/regdata', methods=['post'])
def regdata():
    Username = request.form['name']
    Email = request.form['email']
    Password = request.form['password']
    print(Username, Email, Password)

    for i in c.find():
        if i['email'] == Email:
            return render_template('index.html', err1='you have already registered.')

    session['username'] = Username
    k = {}
    k['name'] = Username
    k['email'] = Email
    k['password'] = Password
    c.insert_one(k)

    return redirect('/dash')

@app.route('/logindata', methods=['POST'])
def logindata():
    Username = request.form.get('name')
    Password = request.form.get('password')
    print(Username, Password)

    if not Username or not Password:
        return render_template('login.html', err2='Please enter both username and password.')

    for i in c.find():
        if i['name'] == Username and i['password'] == Password:
            session['username'] = Username
            return redirect('/dash')

    return render_template('login.html', err='Invalid credentials')

@app.route('/')
def logout():
    session['username'] = None
    return redirect('/')

@app.route('/insertqp', methods=['post'])
def insertqp():
    # Define the question paper document here
    document = {
        # Add the fields here
    }

    # Insert the document into the collection
    c_new.insert_one(document)

    return redirect('/view')

@app.route('/view')
def view():
    sami = db['sami']  # Assuming 'sami' is the collection name
    data = []
    owner = session.get('username')

    if owner is None:
        return render_template('login.html', err1='Please log in first.')

    # Retrieve documents from the collection for the logged-in user
    for doc in c_new.find({'owner': owner}):
        data.append(doc)

    return render_template('new.html', documents=data)

@app.route('/get_collections', methods=['GET'])
def get_collections():
    database = request.args.get('database')
    if database:
        collections = client[database].list_collection_names()
        return jsonify(collections)
    else:
        return jsonify([])

@app.route('/get_databases', methods=['GET'])
def get_databases():
    databases = client.list_database_names()
    return jsonify(databases)

@app.route('/add_collection', methods=['POST'])
def add_collection():
    data = request.get_json()
    database = data.get('database')
    collection = data.get('collection')

    if database and collection:
        try:
            # Create the new collection
            client[database].create_collection(collection)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    else:
        return jsonify({"success": False, "error": "Database or collection name is missing."})
    

@app.route('/remove_collection', methods=['POST'])
def remove_collection():
    data = request.get_json()
    database = data.get('database')
    collection = data.get('collection')

    if database and collection:
        try:
            # Remove the collection
            client[database].drop_collection(collection)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    else:
        return jsonify({"success": False, "error": "Database or collection name is missing."})
    
@app.route('/enter_data.html', methods=['GET'])
def enter_data_html():
    db_name = request.args.get('database')
    collection_name = request.args.get('collection')
    return render_template('enter_data.html', db_name=db_name, collection_name=collection_name)


@app.route('/save_data', methods=['POST'])
def save_data():
    try:
        data = request.get_json()
        database = data.get('database')
        collection = data.get('collection')
        entered_data_list = data.get('data')

        if database and collection and entered_data_list:
            # Save the list of data into the selected collection
            documents = [{'data': item} for item in entered_data_list]
            client[database][collection].insert_many(documents)
            
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Database, collection, or data is missing."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    

@app.route('/here.html', methods=['GET'])
def display_data():
    try:
        database = request.args.get('database')
        collection = request.args.get('collection')

        if database and collection:
            # Fetch data from MongoDB collection excluding deleted items
            deleted_items_ids = request.args.getlist('deleted_items')
            deleted_items_ids = [ObjectId(item_id) for item_id in deleted_items_ids]
            filter_criteria = {"_id": {"$nin": deleted_items_ids}}
            data = client[database][collection].find(filter_criteria)

            # Render the here.html template with the filtered data
            return render_template('here.html', data=data, database=database, collection=collection)
        else:
            return jsonify({"success": False, "error": "Database or collection name is missing."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/delete_data', methods=['POST'])
def delete_data():
    try:
        data = request.get_json()
        database = data.get('database')
        collection = data.get('collection')
        item_id = data.get('itemId')

        if database and collection and item_id:
            item_id = ObjectId(item_id)
            result = client[database][collection].delete_one({"_id": item_id})

            if result.deleted_count == 1:
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "error": "Document not found."})
        else:
            return jsonify({"success": False, "error": "Database, collection, or item ID is missing."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/update_data', methods=['POST'])
def update_data():
    try:
        data = request.get_json()
        database = data.get('database')
        collection = data.get('collection')
        item_id = data.get('itemId')
        updated_data = data.get('updatedData')

        if database and collection and item_id and updated_data:
            item_id = ObjectId(item_id)
            result = client[database][collection].update_one({"_id": item_id}, {"$set": {"data": updated_data}})

            if result.modified_count == 1:
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "error": "Document not found or data not updated."})
        else:
            return jsonify({"success": False, "error": "Database, collection, item ID, or updated data is missing."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
#mapping the years and the subjects total mapping here

db = client['years']
tagged_collection = db['tagged_databases']

# Function to update tagged_databases based on current collections
def update_tagged_databases():
    collections = db.list_collection_names()
    collections = [coll for coll in collections if coll != 'tagged_databases']

    tagged_databases.clear()

    for coll_name in collections:
        collection = db[coll_name]
        databases = set(collection.distinct('database'))
        tagged_databases.update(databases)

    # Update the 'tagged_databases' collection with the new set of tagged databases
    tagged_collection.replace_one({}, {'database': list(tagged_databases)}, upsert=True)

# Initialize tagged_databases set with existing data from the collection
tagged_databases = set(tagged_collection.distinct('database'))

def send_update():
    # Send real-time update to connected clients (if using Flask-SocketIO)
    pass

@app.route('/')
def home():
    return render_template('map.html')

@app.route('/yearcollections')
def getsyears():
    # Update tagged_databases before fetching collections
    update_tagged_databases()

    collections = db.list_collection_names()

    # Exclude specific collection 'tagged_databases' from the list of collections
    collections = [coll for coll in collections if coll != 'tagged_databases']

    return jsonify(collections)

@app.route('/attachdatabases')
def getalldsb():
    # Update tagged_databases before fetching databases
    update_tagged_databases()

    databases = client.list_database_names()

    # Exclude system databases and other MongoDB internal databases
    available_databases = [db for db in databases if db != 'admin' and db != 'config' and db != 'local' and db != 'years' and db!='collage']

    # Include only databases that are present in other collections
    available_databases = [db for db in available_databases if db in tagged_databases]

    return jsonify(available_databases)

@app.route('/save-mapping', methods=['POST'])
def save_mapping():
    data = request.json
    collection_name = data.get('collection')
    selected_databases = data.get('databases')
    selected_semester = data.get('semester')

    try:
        # Check if any selected database is already tagged
        if any(db in tagged_databases for db in selected_databases):
            return jsonify({'success': False, 'message': 'One or more selected databases are already tagged with a collection.'})

        # Insert the mapping information as a document in the selected collection
        selected_collection = db[collection_name]
        mapping_data = {
            'database': selected_databases,
            'collection_name': collection_name,
            'semester': selected_semester  # Include the selected semester in the mapping data
        }
        selected_collection.insert_one(mapping_data)

        # Update tagged_databases after saving mapping
        update_tagged_databases()

        send_update()  # Send real-time update to connected clients

        return jsonify({'success': True, 'message': 'Mapping saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/getallcollections')
def getallcollections():
    # Update tagged_databases before fetching databases
    update_tagged_databases()

    databases = client.list_database_names()

    # Exclude system databases and other MongoDB internal databases
    available_databases = [db for db in databases if db != 'admin' and db != 'config' and db != 'local' and db != 'years' and db != 'collage']

    # Exclude tagged databases from the list of available databases
    available_databases = [db for db in available_databases if db not in tagged_databases]

    return jsonify(available_databases)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)