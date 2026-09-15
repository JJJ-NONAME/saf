To build the *pb2*.py files in the root of the GLOW repo run the following:

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. tests/mocks/mock_products/grpc_mock_product.proto
