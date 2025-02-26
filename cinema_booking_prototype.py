import re
import sys
import utility as utils

logger = utils.get_logger("cinema_bookings")


class CinemaBookingSystem:
    
    UNICODE_A = ord('A')
    
    def __init__(self):
        self.movie_title = None
        self.no_of_rows = 0
        self.seats_per_row = 0
        self.total_seats = 0
        self.bookings = {}
        self.booking_id = "GIC0000"
        
    def generate_unique_id(self):
        prefix = "GIC"
        try:
            match = re.search(rf"{prefix}(\d{{4}})", self.booking_id)
            if not match:
                logger.error("Error generating booking id, invalid booking id format")
                return None
            else:
                next_booking_number = int(match.group(1)) + 1
                next_booking_id = f"{prefix}{next_booking_number:04d}"
                self.booking_id = next_booking_id
                logger.info(f"Generated booking id: {next_booking_id}")
                return next_booking_id
        except Exception:
            logger.error("Error generating booking id", exc_info=True)  
        
    def get_movie_info(self):
        while True:
            try:
                movie_info = input(
                        "Please define movie title and seating map in [Title] [Row] [SeatsPerRow] format:\n"
                        "> "
                )
                
                # Validate [Title] [Row] [SeatsPerRow], including titles with spaces and digits
                match = re.match(r'(.+?)\s+(\d+)\s+(\d+)$', movie_info)
                if not match:
                    raise ValueError("Invalid input format")

                movie_title = match.group(1).title()
                no_of_rows = int(match.group(2))
                seats_per_row = int(match.group(3))
                
                # Assumes that there's a minimum of 5 rows and seats, not given in the exercise
                if 5 <= no_of_rows <= 26 and 5 <= seats_per_row <= 50:
                        self.movie_title = movie_title
                        self.no_of_rows = no_of_rows
                        self.seats_per_row = seats_per_row
                        logger.info(
                            f"Movie {self.movie_title} has been added with {self.no_of_rows} rows and {self.seats_per_row} seats per row"
                        )
                        break
                else:
                    logger.error(
                        f"Invalid input, {no_of_rows} rows and {seats_per_row} seats per row is not within the range of 5 and 26, 5 and 50 respectively"
                    )
                    print(
                        "Invalid input, Please ensure that the number of rows is between 5 and 26, the number of seats per a row is between 5 and 50"
                    )
            except ValueError:
                logger.error("Error getting movie information", exc_info=True)
                print(
                    "Invalid input format, Please define movie title and seating map in [Title] [Row] [SeatsPerRow] format:"
                )

    def is_seat_booked(self, row_index, seat_number):
        """Check whether a seat is booked."""

        row_letter = chr(self.UNICODE_A + row_index)
        for booked_seats in self.bookings.values():
            for seat in booked_seats:
                if seat['row'] == row_letter and seat['seat'] == seat_number:
                    return True      
        return False
           
    def default_seating(self, no_of_tickets):
        """Assign default seating starting from the furthest row and middle-most column."""
        seats = []
        row_index = 0
    
        while no_of_tickets > 0:
            seat_number = max( 1, (self.seats_per_row // 2) - (no_of_tickets // 2) + 1)
            while seat_number <= self.seats_per_row and no_of_tickets > 0:
                if not self.is_seat_booked(row_index, seat_number):
                    seats.append({'row': chr(self.UNICODE_A + row_index), 'seat': seat_number})
                    no_of_tickets -= 1
                seat_number += 1
            row_index += 1

        self.bookings[self.booking_id] = seats
        print(f"Successfully reserved {no_of_tickets} {self.movie_title} tickets.")
        logger.info(f"Booking {self.booking_id} has been made with {seats} seats.")
        
    def change_seating(self, match, no_of_tickets):
        """Change seating based on user input."""
        start_row = match.group(1)
        start_seat = int(match.group(2))
        row_index = ord(start_row) - self.UNICODE_A
        seat_number = start_seat
        
        if seat_number < 1 or seat_number > self.seats_per_row:
            logger.error(f"Invalid seat number: {start_row}{start_seat}")
            print(f"Invalid seat number: {start_row}{start_seat}")
            return

        # Taking a backup and removing the original booking
        original_seats = self.bookings.pop(self.booking_id, [])

        seats = []
        while no_of_tickets > 0:
            while seat_number <= self.seats_per_row and no_of_tickets > 0:
                if not self.is_seat_booked(row_index, seat_number):
                    seats.append({'row': chr(self.UNICODE_A + row_index), 'seat': seat_number})
                    no_of_tickets -= 1
                seat_number += 1
            row_index += 1
            seat_number = 1 

            if no_of_tickets > 0 and seat_number == 1:
                seat_number = max(1, (self.seats_per_row // 2) - (no_of_tickets // 2) + 1)

        if no_of_tickets > 0:
            self.bookings[self.booking_id] = original_seats
            logger.error("Unable to change booking due to insufficient seats.")
            print("Unable to change booking due to insufficient seats.")
        else:
            self.bookings[self.booking_id] = seats
            logger.info(f"Booking {self.booking_id} has been changed with {seats} seats.")
                 
    def generate_seating_map(self, booking_id):
        """Prints the seating arrangement as a grid."""
        
        if booking_id in self.bookings:
            seats = self.bookings[booking_id]
            print(f"Booking id: {self.booking_id}")
            print("S C R E E N")
            print("--------------------------------")

            grid = []
            for i in range(self.no_of_rows):
                row = []
                for j in range(self.seats_per_row):
                    row.append(' .')
                grid.append(row)

            # Marking already booked seats with 'x'
            for booked_id, booked_seats in self.bookings.items():
                for seat in booked_seats:
                    row_index = ord(seat['row']) - self.UNICODE_A
                    seat_number = seat['seat']
                    if 0 <= row_index < self.no_of_rows and 1 <= seat_number <= self.seats_per_row:
                        grid[row_index][seat_number - 1] = ' x'

            # Marking seats for the given booking ID with 'o'
            for seat in seats:
                row_index = ord(seat['row']) - self.UNICODE_A
                seat_number = seat['seat']
                if 0 <= row_index < self.no_of_rows and 1 <= seat_number <= self.seats_per_row:
                    grid[row_index][seat_number - 1] = ' o'
            
            # Print row letters in reverse alphabetical order
            for i in range(self.no_of_rows - 1, -1, -1):
                row_label = chr(self.UNICODE_A + i)
                row_seats = ''
                for seat in grid[i]:
                    row_seats += seat + ' '
                print(row_label + ' ' + row_seats.strip())

            # Print seat numbers
            seat_numbers = ' '
            for i in range(self.seats_per_row):
                seat_numbers += str(i + 1) + '  '
            print('  ' + seat_numbers.strip())
            
            logger.info(f"Seating map generated for booking id: {booking_id}")
        else:
            print(f"Booking ID {booking_id} not found.")
            
    def check_bookings(self):
        """Allows the user to enter their booking ID and see the selected seats in the seating map."""
        
        booking_id = input(
            "Please enter your booking ID:  \n"
            "> "
        )

        if booking_id in self.bookings:
            self.generate_seating_map(booking_id)
        else:
            print(f"Booking ID {booking_id} not found.")
            
    def book_tickets(self):
        """Handles the bookings flow"""
        
        while True:
            try:
                no_of_tickets = input(
                    "Enter number of tickets to book, or enter blank to go back to main menu:  \n"
                    "> "
                )
                if no_of_tickets:
                    no_of_tickets = int(no_of_tickets)
                    if no_of_tickets > self.total_seats:
                        print(f"Sorry, there are only {self.total_seats} seats available.")
                        logger.error(f"Insufficient seats available, only {self.total_seats} seats left.")
                    else:
                        self.generate_unique_id()
                        self.default_seating(no_of_tickets)
                        self.generate_seating_map(self.booking_id)
                        
                        while True:
                            seat_change_response = input(
                                "Enter blank to accept seat selection, or enter new seating position:  \n"
                                "> "
                            )
                            if seat_change_response:
                                # Validate seat position format
                                match = re.match(r"([A-Z]+)(\d+)", seat_change_response)
                                if match:
                                    self.change_seating(match, no_of_tickets)
                                    self.generate_seating_map(self.booking_id)
                                else:
                                    print("Invalid seat position format. Please enter in the format [Row][SeatNumber] (e.g., A01).")
                            else:
                                break
                            
                        self.total_seats -= no_of_tickets
                        print(f"Booking id: {self.booking_id} confirmed.")
                        break

                else:
                    break
            except Exception:
                logger.error("Error in booking tickets", exc_info=True)
                print("Invalid input, Please try again.")
    
    def exit_program(self):
        print(f"Thank you for using GIC Cinemas system. Bye!")
        logger.info("Exiting the program.")
        sys.exit(0)
        
    def booking_menu(self):
        self.get_movie_info()
        self.total_seats = self.no_of_rows * self.seats_per_row

        while True:
            user_selection = input(
                "Welcome to GIC Cinemas \n"
                "[1] Book tickets for "+ self.movie_title + " ("+ str(self.total_seats)+ " seats available) \n"
                "[2] Check bookings \n"
                "[3] Exit  \n"
                "Please enter your selection:  \n"
                "> "
            )

            match user_selection:
                case "1":
                    self.book_tickets()
                case "2":
                    self.check_bookings()
                case "3":
                    self.exit_program()
                case _:
                    print("Invalid selection, Please refer the instructions again.")
                      
if __name__ == "__main__":
    cinema = CinemaBookingSystem()
    cinema.booking_menu()