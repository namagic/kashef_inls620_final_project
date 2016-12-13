Resources
•	food: intended to be a food listing that provides links to food item
•	order: intended to show list of orders that links to specific orders that allows someone to change

Representations
•	Food Listing: this page is supposed to display the form for submitting a new food item as well as the current food items; however, I could not get the page to display food items. I keept receiving a BuildError in the function render_helprequest_as_html whenever I included a line fooditems=fooditems that should have rendered the display of the food items in my JSON file.
•	Food Items: On the food listing page, there are supposed to be links for each of the food items. On this page there would be the option to PATCH a food item. To PATCH, the choices would be say it is still "available" or there is "no more"
•	Order Listing: this html page provides a list of all the orders and allows someone to PATCH an order
•	Order Item: this html page provides a specific order and allows the seller to change the state of the transaction and for the buyer to change the order


Class Attributes

•	food: food item in a list of food
•	order: order that somebody makes

Rel Attributes
•	collection: identifies target resource that represents a collection of which the context resource is a member [RFC 6573]
•	item: the target IRI points to a resource that is a member of the collection represented by the context IRI [RFC 6573]
•	food: refers to specific food

Types
•	foodlisting: this type provides the collection
•	FoodItem: this type provides the actual food item

Properties

•	id: randomly generated code to provide unique id
•	food: food item in a list of food
•	quantity: amount of food available
•	seller: person selling food
•	date_posted: date that seller listed food
•	transaction: the state of the transaction
•	price: amount per pound

NOTES

I realized that if I wanted to actually submit something functional, I needed to use a similar structure to what was already in the helpdesk. I ran into a few bugs that I ultimately didn’t know how to solve.

Here is one bug that I kept running into that didn't allow me to test out other features of the site. I played around quite a bit in the helpdesk example and could change things; however, that fooditems=fooditems kept crashing the site.

def render_helprequest_list_as_html(fooditems):
    return render_template(
        'helprequests+microdata+rdfa.html',
        fooditems=fooditems,
        transactions=TRANSACTION)

I kept getting a BuildError issue which I have not uncovered before in my experience with python. If I removed that fooditems=fooditems line which my understanding it’s intended to show my jsonld data, it will work, but then my html page no longer shows my data which is then useless.

Also, I couldn't add notes to the JSON file, so here is the other class I had created:

//    "orders"
//    { "@type": "orders:Order",
//      "@id": "request/fhs6jo",
//      "food-order" : "Tangerine",
//      "quantity-order" : "5 lbs",
//      "buyer" : "Mr. Green",
//      "date-bought" : "2016-10-13T12:00:4",
//      "transaction": 4,
//
