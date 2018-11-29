
// TransactionProject/BookTrip.java
// See also TransactionProject/index.jsp

import java.io.*;
import java.sql.*;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;
/**
 *
 * This is an example using local transactions. 
 */
@WebServlet(urlPatterns = {"/BookTrip"})
public class BookTrip extends HttpServlet {

    public static String bookStatus = "";
    
    protected void processRequest(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException, ClassNotFoundException, SQLException {
        response.setContentType("text/html;charset=UTF-8");
        try (PrintWriter out = response.getWriter()) {
            
            // Find the make and model of the car that they want.
            String requestMake = request.getParameter("carMake");
            String requestModel = request.getParameter("carModel");
            // Did the user provide these parameters? If not, display front page.
            if(requestMake == null || requestMake.equals("") || requestModel == null || requestModel.equals("")) {
                  response.sendRedirect("index.jsp"); 
                  return;
            }
            // Assume one car is required.
            int requestCarInt = 1;
            
            // Find the plane ID and the required number of seats.
            String requestPlaneId = request.getParameter("planeID");
            String requestPlaneSeats = request.getParameter("planeSeats");
            
             // Did the user provide these parameters? If not, display front page.
            if(requestPlaneId == null || requestPlaneId.equals("") || requestPlaneSeats == null || requestPlaneSeats.equals("")) {
                  response.sendRedirect("index.jsp"); 
                  return;
            }
            // Try to parse requestPlaneSeats as an int.
            // If not possible then display front page.
            int requestPlaneSeatsInt = 0;
            try {
                  requestPlaneSeatsInt = new Integer(requestPlaneSeats).intValue();
            }
            catch(Exception e) {
               response.sendRedirect("index.jsp");
               return;
                
            }
           
            // First read and then make updates to the database.
            
            // Make sure the driver is loaded. 
            Class.forName("org.apache.derby.jdbc.ClientDriver");
            // Establish a connection with credentials.
            Connection con  = DriverManager.getConnection("jdbc:derby://localhost:1527/TripDatabase","UserNamePassIsSesame","Sesame");
            
            // Create an SQL statement that finds the record with the provided plane ID
            int currentSeats = 0;
            PreparedStatement planeBookingStatement = null;
            try{  // try to find seats available on this plane
                  planeBookingStatement = con.prepareStatement("select * from APP.PLANESEATS where ID = " +requestPlaneId);
                  ResultSet planeRs = planeBookingStatement.executeQuery();
                  planeRs.next();
                  currentSeats = planeRs.getInt(2);
               }
               catch(Exception e){
                 // the plane ID lookup was unsuccessful
                 response.sendRedirect("index.jsp");
                 return;
             }
             System.out.println("Available plane seats = " + currentSeats);
             
             PreparedStatement carBookingStatement = null;
             int currentCars = 0;
             
             try { // try to find number of cars available of this make and model      
                carBookingStatement = con.prepareStatement("select * from APP.CARS where make ='" +requestMake + "' and " + "MODEL='"+requestModel+"'");
                ResultSet carRs = carBookingStatement.executeQuery();
                carRs.next();
                currentCars = carRs.getInt(4);
             }
             catch(Exception e){
                 // the make and model lookup was unsuccessful
                 response.sendRedirect("index.jsp");
                 return;
             }
             
             
             try { // book the trip
                 
                 // Use a transaction, we may need to roll it back.
                 // (autocommit == true) => a commit on each execute
                 // (autocommit == false) => wait until the commit occurs
                 con.setAutoCommit(false);
             
                 planeBookingStatement = con.prepareStatement("update APP.PLANESEATS set onhand = " + (currentSeats - requestPlaneSeatsInt) + "where ID = " +requestPlaneId);
                 planeBookingStatement.executeUpdate();
                
                 carBookingStatement = con.prepareStatement("update APP.CARS set onhand = " + (currentCars - requestCarInt) + " where make ='" +requestMake + "' and MODEL='"+requestModel+"'");
                 carBookingStatement.executeUpdate();
                 con.commit();
             }
             catch (SQLException e ) {
                System.out.println("Exception thrown " + e);
                if (con != null) {
                   try {
                       System.err.print("This transaction is being rolled back");
                       con.rollback();
                    } catch(SQLException excep) {
                       System.out.println("Exception on rollback "+ excep);
                    }
                }
            } 
            finally // close all connections
                 {
                     if (planeBookingStatement  != null) {
                         planeBookingStatement.close();
                     }
                     if (carBookingStatement != null) {
                         carBookingStatement.close();
                     }
                     if (con != null) {
                     con.close();
                 }
            }
           response.sendRedirect("index.jsp");
        }
    }

    // <editor-fold defaultstate="collapsed" desc="HttpServlet methods. Click on the + sign on the left to edit the code.">
    /**
     * Handles the HTTP <code>GET</code> method.
     *
     * @param request servlet request
     * @param response servlet response
     * @throws ServletException if a servlet-specific error occurs
     * @throws IOException if an I/O error occurs
     */
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        try {
            processRequest(request, response);
        } catch (ClassNotFoundException ex) {
            Logger.getLogger(BookTrip.class.getName()).log(Level.SEVERE, null, ex);
        } catch (SQLException ex) {
            Logger.getLogger(BookTrip.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    /**
     * Handles the HTTP <code>POST</code> method.
     *
     * @param request servlet request
     * @param response servlet response
     * @throws ServletException if a servlet-specific error occurs
     * @throws IOException if an I/O error occurs
     */
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        try {
            processRequest(request, response);
        } catch (ClassNotFoundException ex) {
            Logger.getLogger(BookTrip.class.getName()).log(Level.SEVERE, null, ex);
        } catch (SQLException ex) {
            Logger.getLogger(BookTrip.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    /**
     * Returns a short description of the servlet.
     *
     * @return a String containing servlet description
     */
    @Override
    public String getServletInfo() {
        return "Short description";
    }// </editor-fold>

}
