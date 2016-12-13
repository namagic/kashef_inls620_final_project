from flask import Flask, render_template, make_response, redirect
from flask.ext.restful import Api, Resource, reqparse, abort

import json
import string
import random
from datetime import datetime

# Define our priority levels.
# These are the values that the "priority" property can take on a help request.
TRANSACTION = ('order requested', 'order purchased', 'seller paid', 'completed', "no more", "available")

# Load data from disk.
# This simply loads the data from our "database," which is just a JSON file.
with open('data.jsonld') as data:
    data = json.load(data)


# Generate a unique ID for a new help request.
# By default this will consist of six lowercase numbers and letters.
def generate_id(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Respond with 404 Not Found if no help request with the specified ID exists.
def error_if_fooditem_not_found(fooditem_id):
    if fooditem_id not in data['fooditems']:
        message = "No food item with ID: {}".format(fooditem_id)
        abort(404, message=message)


# Filter and sort a list of fooditems.
def filter_and_sort_fooditems(query='', sort_by="date_posted"):

    # Returns True if the query string appears in the help request's
    # title or description.
    def matches_query(item):
        (fooditem_id, fooditem) = item
        text = fooditem['food'] + fooditem['date_posted']
        return query.lower() in text

    # Returns the help request's value for the sort property (which by
    # default is the "time" property).
    def get_sort_value(item):
        (fooditem_id, fooditem) = item
        return fooditem[sort_by]

    filtered_fooditems= filter(matches_query, data['fooditems'].items())

    return sorted(filtered_fooditems, key=get_sort_value, reverse=True)


# Given the data for a help request, generate an HTML representation
# of that help request.
def render_helprequest_as_html(fooditem):
    return render_template(
        'fooditem.html',
        transactions=reversed(list(enumerate(TRANSACTION))))

# Given the data for a list of help requests, generate an HTML representation
# of that list.
def render_helprequest_list_as_html(fooditems):
    return render_template(
        'fooditems.html',
        transactions=TRANSACTION)


# Raises an error if the string x is empty (has zero length).
def nonempty_string(x):
    s = str(x)
    if len(x) == 0:
        raise ValueError('string is empty')
    return s


# Specify the data necessary to create a new help request.
# "from", "title", and "description" are all required values.
new_helprequest_parser = reqparse.RequestParser()
for arg in ['seller', 'food', 'quantity']:
    new_helprequest_parser.add_argument(
        arg, type=nonempty_string, required=True,
        help="'{}' is a required value".format(arg))


# Specify the data necessary to update an existing help request.
# Only the priority and comments can be updated.
update_helprequest_parser = reqparse.RequestParser()
update_helprequest_parser.add_argument(
    'transaction', type=int, default=TRANSACTION.index('order requested'))
update_helprequest_parser.add_argument(
    'price', type=str, default='')


# Specify the parameters for filtering and sorting help requests.
# See `filter_and_sort_helprequests` above.
query_parser = reqparse.RequestParser()
query_parser.add_argument(
    'query', type=str, default='')
query_parser.add_argument(
    'sort_by', type=str, choices=('transaction', 'date_posted'), default='date_posted')


# Define our help request resource.
class HelpRequest(Resource):

    # If a help request with the specified ID does not exist,
    # respond with a 404, otherwise respond with an HTML representation.
    def get(self, fooditem_id):
        error_if_fooditem_not_found(fooditem_id)
        return make_response(
            render_helprequest_as_html(
                data['fooditems'][fooditem_id]), 200)

    # If a help request with the specified ID does not exist,
    # respond with a 404, otherwise update the help request and respond
    # with the updated HTML representation.
    def patch(self, fooditem_id):
        error_if_fooditem_not_found(fooditem_id)
        fooditem = data['fooditems'][fooditem_id]
        update = update_helprequest_parser.parse_args()
        fooditem['transaction'] = update['transaction']
        if len(update['price'].strip()) > 0:
            fooditem.setdefault('price', []).append(update['comment'])
        return make_response(
            render_helprequest_as_html(fooditem), 200)


# Define a resource for getting a JSON representation of a help request.
class HelpRequestAsJSON(Resource):

    # If a help request with the specified ID does not exist,
    # respond with a 404, otherwise respond with a JSON representation.
    def get(self, fooditem_id):
        error_if_fooditem_not_found(fooditem_id)
        fooditem = data['fooditems'][fooditem_id]
        fooditem['@context'] = data['@context']
        return fooditem


# Define our help request list resource.
class HelpRequestList(Resource):

    # Respond with an HTML representation of the help request list, after
    # applying any filtering and sorting parameters.
    def get(self):
        query = query_parser.parse_args()
        return make_response(
            render_helprequest_list_as_html(
                filter_and_sort_fooditems(**query)), 200)

    # Add a new help food listing to the list, and respond with an HTML
    # representation of the updated list.
    def post(self):
        fooditem = new_helprequest_parser.parse_args()
        fooditem_id = generate_id()
        fooditem['@id'] = 'request/' + fooditem_id
        fooditem['@type'] = 'foodlisting:FoodItem'
        fooditem['date_posted'] = datetime.isoformat(datetime.now())
        fooditem['transaction'] = TRANSACTION.index('order requested')
        data['fooditems'][fooditem_id] = fooditem
        return make_response(
            render_helprequest_list_as_html(
                filter_and_sort_fooditems()), 201)


# Define a resource for getting a JSON representation of the help request list.
class HelpRequestListAsJSON(Resource):
    def get(self):
        return data

    # I wasn't sure how to make a new functioning class and it kept crashing my site, so I've left this commented out.
    # class ordersList(Resource):
    #     # Respond with an HTML representation of the help request list, after
    #     # applying any filtering and sorting parameters.
    #     def get(self):
    #         query = query_parser.parse_args()
    #         return make_response(
    #             render_helprequest_list_as_html(
    #                 filter_and_sort_fooditems(**query)), 200)
    #
    #     # Add a new help food listing to the list, and respond with an HTML
    #     # representation of the updated list.
    #     def post(self):
    #         orderitem = new_helprequest_parser.parse_args()
    #         orderitem = generate_id()
    #         orderitem['@id'] = 'request/' + orderitem_id
    #         orderitem['@type'] = 'foodlisting:FoodItem'
    #         orderitem['date_posted'] = datetime.isoformat(datetime.now())
    #         orderitem['transaction'] = TRANSACTION.index('order requested')
    #         data['orderitems'][orderitem_id] = orderitem
    #         return make_response(
    #             render_helprequest_list_as_html(
    #                 filter_and_sort_fooditems()), 201)

# Assign URL paths to our resources.
app = Flask(__name__)
api = Api(app)
api.add_resource(HelpRequestList, '/requests')
api.add_resource(HelpRequestListAsJSON, '/requests.json')
api.add_resource(HelpRequest, '/request/<string:fooditem_id>')
api.add_resource(HelpRequestAsJSON, '/request/<string:fooditem_id>.json')
#api.add_resource(ordersList, '/requests')
#api.add_resource(ordersListAsJSON, '/request/<string:orderitem_id>.json')


# Redirect from the index to the list of help requests.
@app.route('/')
def index():
    return redirect(api.url_for(HelpRequestList), code=303)


# This is needed to load JSON from Javascript running in the browser.
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

# Start the server.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
