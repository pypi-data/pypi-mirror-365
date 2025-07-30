/*
* arrayProduct.cpp - example in MATLAB External Interfaces
*
* Multiplies an input scalar (multiplier)
* times a MxN matrix (inMatrix)
* and outputs a MxN matrix (outMatrix)
*
* Usage : from MATLAB
*         >> outMatrix = arrayProduct(multiplier, inMatrix)
*
* This is a C++ MEX-file for MATLAB.
* Copyright 2017 The MathWorks, Inc.
*
*/

#include <mex.hpp>
#include <mexAdapter.hpp>
#include <stdint.h>

#include "movingFilter.h"

class MexFunction : public matlab::mex::Function {
private:
    std::shared_ptr<matlab::engine::MATLABEngine> matlabPtr = getEngine();
    matlab::data::ArrayFactory factory;
public:
    void operator()(matlab::mex::ArgumentList outputs, matlab::mex::ArgumentList inputs) {
        checkArguments(outputs, inputs);
        const uint32_t windowSize = (uint32_t) inputs[0][0];
        matlab::data::TypedArray<double> in = std::move(inputs[1]);
        func(in, windowSize);
        outputs[0] = std::move(in);
    }

    void func(matlab::data::TypedArray<double>& inMatrix, uint32_t windowSize) {
        size_t size = inMatrix.end() - inMatrix.begin();
        double* data = inMatrix.begin().operator->();
        utils::movingFilter(data, data, size,  windowSize / 2, utils::medianFilterKernel);
    }

    void checkArguments(matlab::mex::ArgumentList outputs, matlab::mex::ArgumentList inputs) {


        if (inputs.size() != 2) {
            matlabPtr->feval(u"error", 
                0, std::vector<matlab::data::Array>({ factory.createScalar("Two inputs required") }));
        }

        if (inputs[0].getNumberOfElements() != 1) {
            matlabPtr->feval(u"error", 
                0, std::vector<matlab::data::Array>({ factory.createScalar("Input multiplier must be a scalar") }));
        }
        
        if (inputs[0].getType() != matlab::data::ArrayType::DOUBLE ||
            inputs[0].getType() == matlab::data::ArrayType::COMPLEX_DOUBLE) {
            matlabPtr->feval(u"error", 
                0, std::vector<matlab::data::Array>({ factory.createScalar("Input multiplier must be a noncomplex scalar double") }));
        }

        if (inputs[1].getType() != matlab::data::ArrayType::DOUBLE ||
            inputs[1].getType() == matlab::data::ArrayType::COMPLEX_DOUBLE) {
            matlabPtr->feval(u"error", 
                0, std::vector<matlab::data::Array>({ factory.createScalar("Input matrix must be type double") }));
        }

        if (inputs[1].getDimensions().size() != 2) {
            matlabPtr->feval(u"error", 
                0, std::vector<matlab::data::Array>({ factory.createScalar("Input must be m-by-n dimension") }));
        }
    }
};
