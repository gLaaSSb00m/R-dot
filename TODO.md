# TODO: Make Banner Section Landscape

- [x] Edit .banner class in style.css: change width to 100%, add height: 400px
- [x] Edit .banner img: add height: 100%, object-fit: cover
- [x] Adjust responsive styles in @media (max-width: 768px): change .banner width to 100%, height to 300px
- [x] Adjust responsive styles in @media (max-width: 1024px): change .banner width to 100%
- [x] Verify the changes by running the development server

# TODO: Update Banner Model and Display

- [x] Change Banner model: replace category with type (ForeignKey to Type)
- [x] Update home view: filter banners by type instead of category__type
- [x] Update home.html: remove banner-text div so only image shows
- [x] Run makemigrations and migrate for database changes
- [x] Test banner display on fashion and gadget pages

# TODO: Update Social Login Buttons

- [x] Change social login buttons to be two separate small boxes with black borders - one for Facebook and one for Google, stacked vertically
- [x] Add Google OAuth URLs and views to match Facebook implementation
- [x] Test the signup page to ensure both buttons display correctly
