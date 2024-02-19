from sqlalchemy import Column, Integer, String, ForeignKey,MetaData
from sqlalchemy.orm import relationship,session
from sqlalchemy.ext.declarative import declarative_base

convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

# engine = create_engine('sqlite:///migrations_test.db')
Base = declarative_base(metadata=metadata)

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer(), primary_key=True)
    name = Column(String())
    price = Column(Integer())
    reviews = relationship('Review', back_populates='restaurant')
    
    def __repr__(self):
        return f'Restaurant(id={self.id},'+\
            f'name={self.name},'+\
            f'price={self.price})'
    
    def all_reviews(self):
        reviews = []
        for review in self.reviews:
            customer_name = f"{review.customer.first_name} {review.customer.last_name}"
            review_text = f"Review for {self.name} by {customer_name}: {review.star_rating} stars."
            reviews.append(review_text)
        return reviews
    def fanciest(cls):
        return session.query(cls).order_by(cls.price.desc()).first()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer(), primary_key=True)
    first_name = Column(String())
    last_name = Column(String())
    reviews = relationship('Review', back_populates='customer')

    def __repr__(self):
        return f'Customer(id={self.id},'+\
            f'first_name={self.first_name},'+\
            f'last_name={self.last_name})'
    def full_name(self):
        full=f'{self.first_name}{self.last_name}'
        return full
    def favorite_restaurant(self):
        # Get all reviews by this customer
        customer_reviews = [review for review in self.reviews]
        
        # Find the highest rated restaurant among the customer's reviews
        if customer_reviews:
            highest_rated_review = max(customer_reviews, key=lambda x: x.star_rating)
            return highest_rated_review.restaurant
        else:
            return None 
        
    def add_review(self, restaurant, rating):
        new_review = Review(restaurant=restaurant, customer=self, star_rating=rating)
        session.add(new_review)
        session.commit()

    def delete_reviews(self, restaurant):
        # Get all reviews by this customer for the specified restaurant
        reviews_to_delete = session.query(Review).filter_by(customer_id=self.id, restaurant_id=restaurant.id).all()
        
        # Delete the reviews
        for review in reviews_to_delete:
            session.delete(review)
        session.commit()

    
class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer(), primary_key=True)
    star_rating = Column(Integer())
    restaurant_id = Column(Integer(), ForeignKey('restaurants.id'))
    customer_id = Column(Integer(), ForeignKey('customers.id'))
    restaurant = relationship('Restaurant', back_populates='reviews')
    customer = relationship('Customer', back_populates='reviews')

    def __repr__(self):
        return f'Review(id={self.id},'+\
            f'star_rating={self.star_rating})'
    
    def full_review(self):
        customer_name = f"{self.customer.first_name} {self.customer.last_name}"
        return f"Review for {self.restaurant.name} by {customer_name}: {self.star_rating} stars"
