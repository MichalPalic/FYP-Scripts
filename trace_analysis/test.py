import matplotlib.pyplot as plt

# Sample data
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
sales = [200, 210, 270, 350, 310, 330]

# Creating the line graph
plt.figure(figsize=(8, 4))
plt.plot(list(range(len(sales))), sales)  # 'o' adds markers to each data point
plt.title('Monthly Sales Data')
plt.xlabel('Month')
plt.ylabel('Sales')
# plt.grid(True)
plt.show()
